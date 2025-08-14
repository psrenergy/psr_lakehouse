# PSR Lakehouse Data Explorer

A Streamlit web application for exploring Brazilian energy market data from PSR's data lakehouse.

## Features

- **Hierarchical Data Selection**: Three-level tree structure (Organization → Dataset → Column)
- **Multi-Data Visualization**: Compare multiple datasets and columns on the same chart
- **Interactive Filtering**: Date range and subsystem filters
- **Automatic Frequency Detection**: Identifies hourly, daily, weekly, monthly, or yearly data patterns
- **Real-time Data Fetching**: Direct integration with PSR Lakehouse API
- **Responsive Design**: Works on desktop and mobile devices

## Available Data

### Organizations
- **CCEE**: Brazilian electricity market data
- **ONS**: Transmission operator data

### Datasets
- **CCEE Spot Price**: Hourly electricity spot prices by subsystem
- **ONS Stored Energy**: Reservoir stored energy levels by subsystem  
- **ONS Load Marginal Cost Weekly**: Weekly marginal cost of load by subsystem and load segment

## Installation

1. Install the UI dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have the PSR Lakehouse package installed and configured with proper credentials.

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### How to Use

1. **Select Organization**: Choose between CCEE (electricity market) or ONS (transmission operator)

2. **Choose Dataset**: Select from available datasets for the chosen organization

3. **Pick Columns**: Select one or more data columns you want to visualize

4. **Set Filters**: 
   - Adjust date range to focus on specific time periods
   - Select subsystems to include in the analysis

5. **Add to Visualization**: Click "Add to Visualization" to include the selection in your chart

6. **Compare Data**: Repeat steps 1-5 to add multiple datasets for comparison

7. **Explore**: Use the interactive Plotly chart to zoom, pan, and hover for detailed information

### Features

- **Data Caching**: Automatically caches fetched data for better performance
- **Selection Management**: Add and remove data selections dynamically
- **Data Overview**: View summary statistics and data information
- **Raw Data Access**: Expand the "Raw Data" section to see the underlying DataFrame
- **Responsive Charts**: Charts automatically adjust to different screen sizes

## Data Structure

The application expects data with the following structure:
- **Index**: Multi-index with `reference_date` and `subsystem`
- **Columns**: Various data columns depending on the dataset
- **Frequency**: Automatically detected based on date patterns

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure your AWS credentials are properly configured
2. **No Data Displayed**: Check date filters and subsystem selections
3. **Slow Loading**: Large date ranges may take longer to fetch; consider narrowing the range

### Environment Variables

Make sure these environment variables are set:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `POSTGRES_PASSWORD`

## Architecture

The application is built using:
- **Streamlit**: Web framework for the user interface
- **Plotly**: Interactive charting library
- **PSR Lakehouse**: Data access layer
- **Pandas**: Data manipulation and analysis

## Development

To modify or extend the application:

1. The main application logic is in `app.py`
2. PSR Lakehouse integration uses the `ui_helpers` module
3. Styling is handled through custom CSS in the Streamlit app
4. Data fetching is cached for performance optimization