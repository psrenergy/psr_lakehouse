"""
PSR Lakehouse Data Explorer

A Streamlit application for exploring Brazilian energy market data from PSR's data lakehouse.
Features a hierarchical tree structure for data selection: Organization > Dataset > Column.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import dotenv

dotenv.load_dotenv(override=True)

# Import PSR Lakehouse components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from psr.lakehouse.ui_helpers import (
    get_organizations,
    get_datasets_by_organization,
    get_data_columns,
    fetch_data_by_strings,
    format_column_display_name,
    parse_date_range_for_filters,
    get_subsystems
)




# Page configuration
st.set_page_config(
    page_title="PSR Lakehouse Data Explorer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stSelectbox > div > div > select {
        font-size: 14px;
    }
    .dataset-info {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .column-info {
        background-color: #e8f4fd;
        padding: 8px;
        border-radius: 3px;
        margin: 5px 0;
        border-left: 3px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'selected_data' not in st.session_state:
        st.session_state.selected_data = []
    if 'data_cache' not in st.session_state:
        st.session_state.data_cache = {}


def get_data_frequency(df: pd.DataFrame) -> str:
    """Determine the frequency of the data based on datetime index."""
    if df.empty or 'reference_date' not in df.index.names:
        return "Unknown"
    
    # Get unique dates
    dates = df.index.get_level_values('reference_date').unique()
    if len(dates) < 2:
        return "Single point"
    
    # Calculate time differences
    dates_sorted = pd.to_datetime(dates).sort_values()
    time_diffs = dates_sorted.diff().dropna()
    
    if time_diffs.empty:
        return "Unknown"
    
    # Get the most common time difference using a simpler approach
    # Convert to total seconds and create a Series for mode calculation
    time_diffs_seconds = pd.Series(time_diffs.total_seconds())
    
    if time_diffs_seconds.empty:
        return "Unknown"
    
    # Get mode or use the first difference if mode fails
    try:
        mode_result = time_diffs_seconds.mode()
        mode_diff_seconds = mode_result.iloc[0] if not mode_result.empty else time_diffs_seconds.iloc[0]
    except:
        # Fallback to first difference
        mode_diff_seconds = time_diffs_seconds.iloc[0]
    
    mode_diff = timedelta(seconds=mode_diff_seconds)
    
    if mode_diff <= timedelta(hours=1):
        return "Hourly"
    elif mode_diff <= timedelta(days=1):
        return "Daily"
    elif mode_diff <= timedelta(days=7):
        return "Weekly"
    elif mode_diff <= timedelta(days=31):
        return "Monthly"
    else:
        return "Yearly"


def create_tree_selector():
    """Create the hierarchical tree selector in the sidebar."""
    st.sidebar.header("📊 Data Selection")
    
    # Organization selector
    organizations = get_organizations()
    selected_org = st.sidebar.selectbox(
        "🏢 Organization",
        organizations,
        help="Select the data organization (CCEE for electricity market, ONS for transmission operator)"
    )
    
    if selected_org:
        # Dataset selector
        datasets = get_datasets_by_organization(selected_org)
        if datasets:
            dataset_options = {f"{d['data_name']} - {d['description'][:50]}...": d for d in datasets}
            selected_dataset_display = st.sidebar.selectbox(
                "📈 Dataset",
                list(dataset_options.keys()),
                help="Select the dataset you want to explore"
            )
            
            if selected_dataset_display:
                selected_dataset = dataset_options[selected_dataset_display]
                
                # Column selector (multi-select)
                columns = get_data_columns(selected_dataset['table_name'])
                if columns:
                    column_options = {
                        format_column_display_name(col): col['column_name'] 
                        for col in columns
                    }
                    
                    selected_columns_display = st.sidebar.multiselect(
                        "📊 Columns",
                        list(column_options.keys()),
                        help="Select one or more data columns to visualize"
                    )
                    
                    if selected_columns_display:
                        selected_columns = [column_options[col] for col in selected_columns_display]
                        
                        return selected_org, selected_dataset, selected_columns
    
    return None, None, None


def create_filters_section():
    """Create the filters section in the sidebar (now simplified)."""
    # Subsystem filter only
    try:
        subsystems = get_subsystems()
        selected_subsystems = st.sidebar.multiselect(
            "🔌 Subsystems (Optional)",
            subsystems,
            default=subsystems,
            help="Select electrical subsystems to include"
        )
    except Exception:
        selected_subsystems = None
    
    return selected_subsystems


def add_to_selection(org: str, dataset: dict, columns: List[str]):
    """Add selected data to the current selection."""
    selection_key = f"{org}_{dataset['data_name']}_{','.join(columns)}"
    
    # Check if already selected
    existing_keys = [item['key'] for item in st.session_state.selected_data]
    if selection_key not in existing_keys:
        # Get column descriptions for display
        columns_metadata = get_data_columns(dataset['table_name'])
        column_name_to_description = {
            col['column_name']: col['description'] for col in columns_metadata
        }
        
        # Create display names using descriptions
        column_descriptions = [column_name_to_description.get(col, col) for col in columns]
        
        st.session_state.selected_data.append({
            'key': selection_key,
            'organization': org,
            'dataset': dataset,
            'columns': columns,
            'display_name': f"{org} - {dataset['data_name']} ({', '.join(column_descriptions)})"
        })
        st.success(f"Added: {org} - {dataset['data_name']} ({', '.join(column_descriptions)})")
    else:
        st.warning("This selection is already added!")


def fetch_and_cache_data(selection: dict, subsystems):
    """Fetch data for a selection and cache it."""
    cache_key = f"{selection['key']}_{','.join(subsystems or [])}"
    
    if cache_key in st.session_state.data_cache:
        return st.session_state.data_cache[cache_key]
    
    try:
        # Fetch all data (no date filtering)
        df = fetch_data_by_strings(
            organization=selection['organization'],
            data_name=selection['dataset']['data_name'],
            columns=selection['columns']
        )
        
        # Filter by subsystems if specified
        if subsystems and 'subsystem' in df.index.names:
            df = df[df.index.get_level_values('subsystem').isin(subsystems)]
        
        # Cache the result
        st.session_state.data_cache[cache_key] = df
        return df
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()


def create_visualization(data_dict: Dict[str, pd.DataFrame]):
    """Create Plotly visualization for the selected data."""
    if not data_dict:
        st.info("No data selected for visualization. Please add data using the sidebar.")
        return
    
    # Create subplots or single plot based on data
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    color_idx = 0
    
    for selection_key, df in data_dict.items():
        if df.empty:
            continue
            
        # Get the selection info
        selection = next((item for item in st.session_state.selected_data if item['key'] == selection_key), None)
        if not selection:
            continue
        
        # Get column metadata for user-friendly names
        columns_metadata = get_data_columns(selection['dataset']['table_name'])
        column_name_to_description = {
            col['column_name']: col['description'] for col in columns_metadata
        }
        
        # Get frequency info
        frequency = get_data_frequency(df)
        
        # Handle multi-index (reference_date, subsystem)
        if isinstance(df.index, pd.MultiIndex):
            # Iterate through each subsystem
            for subsystem in df.index.get_level_values('subsystem').unique():
                subsystem_data = df.xs(subsystem, level='subsystem')
                
                for column in selection['columns']:
                    if column in subsystem_data.columns:
                        # Use description for display name
                        display_name = column_name_to_description.get(column, column)
                        legend_name = f"{selection['organization']} - {display_name} ({subsystem})"
                        
                        fig.add_trace(
                            go.Scatter(
                                x=subsystem_data.index,
                                y=subsystem_data[column],
                                mode='lines+markers',
                                name=legend_name,
                                line=dict(color=colors[color_idx % len(colors)]),
                                hovertemplate=f"<b>{display_name} ({subsystem})</b><br>Date: %{{x}}<br>Value: %{{y}}<br>Frequency: {frequency}<extra></extra>"
                            )
                        )
                        color_idx += 1
        else:
            # Simple index
            for column in selection['columns']:
                if column in df.columns:
                    # Use description for display name
                    display_name = column_name_to_description.get(column, column)
                    legend_name = f"{selection['organization']} - {display_name}"
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[column],
                            mode='lines+markers',
                            name=legend_name,
                            line=dict(color=colors[color_idx % len(colors)]),
                            hovertemplate=f"<b>{display_name}</b><br>Date: %{{x}}<br>Value: %{{y}}<br>Frequency: {frequency}<extra></extra>"
                        )
                    )
                    color_idx += 1
    
    # Update layout
    fig.update_layout(
        title="PSR Lakehouse Data Visualization",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Sidebar selectors
    org, dataset, columns = create_tree_selector()
    subsystems = create_filters_section()
    
    # Add to selection button
    if org and dataset and columns:
        if st.sidebar.button("➕ Add to Visualization", type="primary"):
            add_to_selection(org, dataset, columns)
    
    # Current selections management
    if st.session_state.selected_data:
        st.sidebar.header("📋 Current Selections")
        
        # Display current selections with remove option
        for i, selection in enumerate(st.session_state.selected_data):
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.write(f"**{i+1}.** {selection['display_name']}")
            with col2:
                if st.button("🗑️", key=f"remove_{i}", help="Remove this selection"):
                    st.session_state.selected_data.pop(i)
                    st.rerun()
        
        # Clear all button
        if st.sidebar.button("🗑️ Clear All", type="secondary"):
            st.session_state.selected_data = []
            st.session_state.data_cache = {}
            st.rerun()
    
    # Main content area
    if st.session_state.selected_data:
        # Fetch data for all selections
        data_dict = {}
        
        with st.spinner("Fetching data..."):
            for selection in st.session_state.selected_data:
                df = fetch_and_cache_data(selection, subsystems)
                if not df.empty:
                    data_dict[selection['key']] = df
        
        # Display data info
        if data_dict:
            st.header("📈 Data Overview")
            
            # Data summary
            col1, col2, col3 = st.columns(3)
            
            total_records = sum(len(df) for df in data_dict.values())
            unique_dates = set()
            frequencies = set()
            
            for df in data_dict.values():
                if not df.empty and 'reference_date' in df.index.names:
                    dates = df.index.get_level_values('reference_date').unique()
                    unique_dates.update(dates)
                    frequencies.add(get_data_frequency(df))
            
            with col1:
                st.metric("Total Records", total_records)
            with col2:
                st.metric("Date Range", f"{len(unique_dates)} unique dates")
            with col3:
                st.metric("Data Frequencies", ", ".join(frequencies))
        
        # Create visualization
        st.header("📊 Visualization")
        create_visualization(data_dict)
        
        # Data table (expandable)
        with st.expander("📋 Raw Data", expanded=False):
            for selection_key, df in data_dict.items():
                selection = next((item for item in st.session_state.selected_data if item['key'] == selection_key), None)
                if selection:
                    st.subheader(f"{selection['organization']} - {selection['dataset']['data_name']}")
                    st.dataframe(df, use_container_width=True)
    
    else:
        # Welcome message
        st.info("""
        👋 Welcome to the PSR Lakehouse Data Explorer!
        
        **Getting Started:**
        1. Use the sidebar to select an **Organization** (CCEE or ONS)
        2. Choose a **Dataset** from the available options
        3. Select one or more **Columns** to visualize
        4. Click **"Add to Visualization"** to add the data
        5. Optionally filter by **Subsystems** if needed
        
        The application fetches all available historical data for comprehensive analysis.
        You can add multiple datasets and columns to compare different metrics on the same chart.
        """)


if __name__ == "__main__":
    main()