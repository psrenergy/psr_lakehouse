"""
Example usage of UI helper functions for Streamlit integration.

This example demonstrates how to use the new UI helper functions
to create selectors and retrieve data in a Streamlit application.
"""

from datetime import date, datetime

import pandas as pd
import streamlit as st

# Import the UI helper functions
from psr.lakehouse import (
    fetch_data_by_strings,
    format_column_display_name,
    get_data_columns,
    get_datasets_by_organization,
    get_organizations,
    get_streamlit_selector_options,
    get_subsystems,
    parse_date_range_for_filters,
)


def main():
    """Main Streamlit application."""
    st.title("PSR Lakehouse Data Explorer")
    st.write("Explore Brazilian energy market data from CCEE and ONS")

    # Method 1: Individual selector functions
    st.header("Method 1: Individual Selectors")

    # Organization selector
    organizations = get_organizations()
    selected_org = st.selectbox("Select Organization:", organizations, key="org1")

    # Dataset selector (filtered by organization)
    if selected_org:
        datasets = get_datasets_by_organization(selected_org)
        dataset_names = [d["data_name"] for d in datasets]
        selected_dataset = st.selectbox("Select Dataset:", dataset_names, key="dataset1")

        if selected_dataset:
            # Get the table name for the selected dataset
            selected_table = next(d["table_name"] for d in datasets if d["data_name"] == selected_dataset)

            # Column selector
            columns = get_data_columns(selected_table)
            if columns:
                column_options = [format_column_display_name(col) for col in columns]
                selected_columns_display = st.multiselect("Select Columns:", column_options, key="cols1")

                # Convert back to column names
                selected_columns = []
                for display_name in selected_columns_display:
                    for col in columns:
                        if format_column_display_name(col) == display_name:
                            selected_columns.append(col["column_name"])
                            break

    # Method 2: Get all options at once (more efficient)
    st.header("Method 2: Efficient All-at-Once Loading")

    # Get all selector options in one call
    options = get_streamlit_selector_options()

    # Organization selector
    selected_org2 = st.selectbox("Select Organization:", options["organizations"], key="org2")

    # Dataset selector (client-side filtering)
    if selected_org2:
        org_datasets = [d for d in options["datasets"] if d["organization"] == selected_org2]
        dataset_names2 = [d["data_name"] for d in org_datasets]
        selected_dataset2 = st.selectbox("Select Dataset:", dataset_names2, key="dataset2")

        if selected_dataset2:
            selected_table2 = next(d["table_name"] for d in org_datasets if d["data_name"] == selected_dataset2)

            # Column selector
            columns2 = get_data_columns(selected_table2)
            if columns2:
                column_options2 = [format_column_display_name(col) for col in columns2]
                selected_columns_display2 = st.multiselect("Select Columns:", column_options2, key="cols2")

    # Additional filters
    st.header("Additional Filters")

    # Subsystem filter (if applicable)
    subsystems = get_subsystems()
    selected_subsystems = st.multiselect("Filter by Subsystems:", subsystems)

    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date:", value=date(2024, 1, 1))
    with col2:
        end_date = st.date_input("End Date:", value=date.today())

    # Fetch data button
    if st.button("Fetch Data") and "selected_org" in locals() and "selected_dataset" in locals():
        try:
            # Prepare filters
            filters = parse_date_range_for_filters(start_date, end_date)

            # Add subsystem filter if selected
            if selected_subsystems:
                # Note: This would need to be implemented in the fetch function
                # For now, we'll filter after fetching
                pass

            # Fetch data using string identifiers
            df = fetch_data_by_strings(
                organization=selected_org,
                data_name=selected_dataset,
                columns=selected_columns if "selected_columns" in locals() else None,
                **filters,
            )

            # Apply subsystem filter if needed
            if selected_subsystems and "subsystem" in df.index.names:
                df = df[df.index.get_level_values("subsystem").isin(selected_subsystems)]

            # Display results
            st.header("Data Results")
            st.write(f"Retrieved {len(df)} rows")
            st.dataframe(df)

            # Basic visualization
            if not df.empty and len(df.columns) > 0:
                st.header("Quick Visualization")
                if len(df.columns) == 1:
                    # Single column - line chart
                    st.line_chart(df)
                else:
                    # Multiple columns - let user select
                    viz_column = st.selectbox("Select column to visualize:", df.columns)
                    if viz_column:
                        st.line_chart(df[viz_column])

            # Export option
            st.header("Export Data")
            if st.button("Export to CSV"):
                csv = df.to_csv()
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_org}_{selected_dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")


def streamlit_integration_examples():
    """
    Additional examples showing different ways to integrate with Streamlit.
    """

    # Example 1: Simple data explorer
    def simple_explorer():
        st.subheader("Simple Data Explorer")

        # Quick way to get data
        org = st.selectbox("Organization:", get_organizations())
        if org:
            datasets = get_datasets_by_organization(org)
            dataset_names = [d["data_name"] for d in datasets]
            dataset = st.selectbox("Dataset:", dataset_names)

            if dataset and st.button("Load Data"):
                df = fetch_data_by_strings(org, dataset)
                st.dataframe(df.head(100))  # Show first 100 rows

    # Example 2: Advanced filtering
    def advanced_filtering():
        st.subheader("Advanced Filtering Example")

        # Multi-step filtering
        with st.form("data_filters"):
            org = st.selectbox("Organization:", get_organizations())

            if org:
                datasets = get_datasets_by_organization(org)
                dataset = st.selectbox("Dataset:", [d["data_name"] for d in datasets])

                # Date range
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")

                # Subsystem selection
                subsystems = st.multiselect("Subsystems:", get_subsystems())

                submitted = st.form_submit_button("Apply Filters")

                if submitted and org and dataset:
                    filters = parse_date_range_for_filters(start_date, end_date)

                    df = fetch_data_by_strings(org, dataset, **filters)

                    if subsystems and "subsystem" in df.index.names:
                        df = df[df.index.get_level_values("subsystem").isin(subsystems)]

                    st.write(f"Filtered data: {len(df)} rows")
                    st.dataframe(df)

    # Example 3: Cached data loading
    @st.cache_data
    def load_cached_data(org: str, dataset: str, start_date: str, end_date: str):
        """Cache data loading for better performance."""
        return fetch_data_by_strings(org, dataset, start_reference_date=start_date, end_reference_date=end_date)

    def cached_explorer():
        st.subheader("Cached Data Explorer")
        st.write("This example uses Streamlit's caching for better performance")

        org = st.selectbox("Organization:", get_organizations(), key="cached_org")
        if org:
            datasets = get_datasets_by_organization(org)
            dataset = st.selectbox("Dataset:", [d["data_name"] for d in datasets], key="cached_dataset")

            if dataset:
                # Use cached loading
                df = load_cached_data(org, dataset, "2024-01-01", "2024-12-31")
                st.dataframe(df)


if __name__ == "__main__":
    # Run the main application
    main()

    # Uncomment to see additional examples
    # st.divider()
    # streamlit_integration_examples()
