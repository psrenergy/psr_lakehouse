API Reference
=============

This page provides detailed documentation of the PSR Lakehouse Client API.

Client Class
------------

The main interface for interacting with the PSR Lakehouse API. The client uses a singleton pattern to ensure only one instance exists throughout your application.

.. code-block:: python

   from psr.lakehouse import client

Initialization
~~~~~~~~~~~~~~

The client is automatically initialized as a singleton. You can configure it using:

.. code-block:: python

   from psr.lakehouse import initialize
   
   initialize(
       base_url="https://api.example.com",
       aws_access_key_id="your-access-key",
       aws_secret_access_key="your-secret-key",
       region="us-east-1",
   )

Or set environment variables before importing:

.. code-block:: bash

   LAKEHOUSE_API_URL="https://api.example.com"
   AWS_ACCESS_KEY_ID="your-access-key"
   AWS_SECRET_ACCESS_KEY="your-secret-key"
   AWS_DEFAULT_REGION="us-east-1"

Data Fetching Methods
----------------------

fetch_dataframe()
~~~~~~~~~~~~~~~~~

Fetch data from the API and return as a pandas DataFrame using a simplified interface.

**Signature:**

.. code-block:: python

   def fetch_dataframe(
       table_name: str,
       indices_columns: list[str] | None = None,
       data_columns: list[str] | None = None,
       filters: dict | None = None,
       start_reference_date: str | None = None,
       end_reference_date: str | None = None,
       group_by: list[str] | None = None,
       aggregation_method: str | None = None,
       datetime_granularity: str | None = None,
       order_by: list[dict] | None = None,
       output_timezone: str = "America/Sao_Paulo",
   ) -> pd.DataFrame

**Parameters:**

* ``table_name`` (str) - Name of the table to query in snake_case format (e.g., ``"ccee_spot_price"``)
* ``indices_columns`` (list[str], optional) - Columns to use as DataFrame index. If not provided, DataFrame will use default integer index.
* ``data_columns`` (list[str], optional) - Data columns to fetch. If not provided along with indices_columns, all columns will be fetched.
* ``filters`` (dict, optional) - Dictionary of column-value pairs for equality filtering (e.g., ``{"subsystem": "SOUTHEAST"}``)
* ``start_reference_date`` (str, optional) - Start date filter in ISO format (inclusive), e.g., ``"2023-05-01"``
* ``end_reference_date`` (str, optional) - End date filter in ISO format (exclusive), e.g., ``"2023-05-02"``
* ``group_by`` (list[str], optional) - List of columns to group by for aggregation
* ``aggregation_method`` (str, optional) - Aggregation method when using ``group_by``. Options: ``"sum"``, ``"avg"``, ``"min"``, ``"max"``
* ``datetime_granularity`` (str, optional) - Temporal aggregation level. Options: ``"hour"``, ``"day"``, ``"week"``, ``"month"``
* ``order_by`` (list[dict], optional) - Sort order as list of dictionaries with ``column`` and ``direction`` (``"asc"`` or ``"desc"``)
* ``output_timezone`` (str, optional) - Output timezone for datetime fields. Default: ``"America/Sao_Paulo"``

**Returns:**

* ``pd.DataFrame`` - Query results as a pandas DataFrame

**Raises:**

* ``LakehouseError`` - If ``group_by`` and ``aggregation_method`` are not provided together, or if an unsupported aggregation method is specified

**Example:**

.. code-block:: python

   # Basic fetch
   df = client.fetch_dataframe(
       table_name="ccee_spot_price",
       indices_columns=["reference_date", "subsystem"],
       data_columns=["spot_price"],
       start_reference_date="2023-05-01",
       end_reference_date="2023-05-02",
   )

   # With filtering
   df = client.fetch_dataframe(
       table_name="ons_stored_energy_subsystem",
       indices_columns=["reference_date"],
       data_columns=["verified_stored_energy_percentage"],
       start_reference_date="2023-05-01",
       end_reference_date="2023-05-02",
       filters={"subsystem": "SOUTHEAST"},
   )

   # With aggregation
   df = client.fetch_dataframe(
       table_name="ccee_spot_price",
       data_columns=["spot_price"],
       start_reference_date="2023-01-01",
       end_reference_date="2023-02-01",
       group_by=["subsystem"],
       aggregation_method="avg",
   )

   # With temporal aggregation
   df = client.fetch_dataframe(
       table_name="ons_power_plant_hourly_generation",
       data_columns=["plant_type", "generation"],
       start_reference_date="2025-01-01",
       end_reference_date="2025-01-31",
       group_by=["reference_date", "plant_type"],
       aggregation_method="sum",
       datetime_granularity="day",
   )

   # With ordering
   df = client.fetch_dataframe(
       table_name="ccee_spot_price",
       data_columns=["spot_price"],
       start_reference_date="2023-01-01",
       end_reference_date="2023-02-01",
       order_by=[
           {"column": "reference_date", "direction": "desc"},
           {"column": "subsystem", "direction": "asc"},
       ],
   )

fetch_dataframe_from_query()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fetch data using a custom JSON query body. This method provides access to advanced features like joins, custom operators, and complex ordering.

**Signature:**

.. code-block:: python

   def fetch_dataframe_from_query(
       json_body: dict,
       page_size: int = 1000
   ) -> pd.DataFrame

**Parameters:**

* ``json_body`` (dict) - JSON request body for the query. See Query Structure below.
* ``page_size`` (int, optional) - Number of results per page. Default: 1000

**Returns:**

* ``pd.DataFrame`` - Query results as a pandas DataFrame

**Query Body Structure:**

The ``json_body`` parameter accepts a dictionary with the following structure:

.. code-block:: python

   {
       "query_data": [
           "ModelName.column1",
           "ModelName.column2"
       ],
       "query_filters": [
           {
               "column": "ModelName.column_name",
               "operator": ">=",  # Operators: =, !=, >, <, >=, <=
               "value": "value"
           }
       ],
       "group_by": {
           "group_by_clause": ["ModelName.column1"],
           "default_aggregation_method": "sum",  # Options: sum, avg, min, max
           "datetime_granularity": "day"  # Options: hour, day, week, month
       },
       "order_by": [
           {
               "column": "ModelName.column_name",
               "direction": "asc"  # or "desc"
           }
       ],
       "joins": [
           {
               "join_model": "OtherModelName",
               "join_filters": [
                   {
                       "column": "ModelName.key_column",
                       "value": "OtherModelName.key_column",
                       "operator": "="
                   }
               ],
               "is_outer_join": False  # or True
           }
       ],
       "output_timezone": "America/Sao_Paulo"
   }

**Notes:**

* Model names use PascalCase (e.g., ``ONSPowerPlantHourlyGeneration``)
* All fields except ``query_data`` are optional
* The method automatically handles pagination and fetches all pages

**Example:**

.. code-block:: python

   df = client.fetch_dataframe_from_query({
       "query_data": [
           "ONSPowerPlantHourlyGeneration.reference_date",
           "ONSPowerPlantHourlyGeneration.plant_type",
           "ONSPowerPlantHourlyGeneration.generation"
       ],
       "group_by": {
           "group_by_clause": [
               "ONSPowerPlantHourlyGeneration.reference_date",
               "ONSPowerPlantHourlyGeneration.plant_type"
           ],
           "default_aggregation_method": "sum",
           "datetime_granularity": "day"
       },
       "query_filters": [
           {
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "operator": ">=",
               "value": "2025-01-01"
           }
       ]
   })

Schema Discovery Methods
-------------------------

list_tables()
~~~~~~~~~~~~~

List all available table names in the API.

**Signature:**

.. code-block:: python

   def list_tables() -> list[str]

**Returns:**

* ``list[str]`` - Sorted list of table names in PascalCase (e.g., ``["CCEESpotPrice", "ONSEnergyLoadDaily", ...]``)

**Example:**

.. code-block:: python

   tables = client.list_tables()
   print(f"Available tables: {len(tables)}")
   for table in tables[:10]:
       print(f"  - {table}")

get_schema()
~~~~~~~~~~~~

Get detailed schema information for a specific table.

**Signature:**

.. code-block:: python

   def get_schema(table_name: str) -> dict

**Parameters:**

* ``table_name`` (str) - Table name in snake_case or PascalCase (e.g., ``"ccee_spot_price"`` or ``"CCEESpotPrice"``)

**Returns:**

* ``dict`` - Dictionary mapping field names to their metadata. Each field contains:
  
  * ``type`` (str) - Field type: ``string``, ``integer``, ``number``, ``enum``, ``boolean``, etc.
  * ``nullable`` (bool) - Whether the field can be null
  * ``title`` (str, optional) - Human-readable field name
  * ``description`` (str, optional) - Field description
  * ``format`` (str, optional) - Format specification (e.g., ``date-time``)
  * ``enum_values`` (list[str], optional) - Allowed values for enum fields

**Example:**

.. code-block:: python

   schema = client.get_schema("ccee_spot_price")
   
   for field_name, field_info in schema.items():
       print(f"\n{field_name}:")
       print(f"  Type: {field_info['type']}")
       print(f"  Nullable: {field_info['nullable']}")
       
       if 'description' in field_info:
           print(f"  Description: {field_info['description']}")
       
       if 'enum_values' in field_info:
           print(f"  Allowed values: {field_info['enum_values']}")

**Example Output:**

.. code-block:: python

   {
       'id': {
           'type': 'integer',
           'nullable': True,
           'title': 'Id'
       },
       'reference_date': {
           'type': 'string',
           'nullable': False,
           'format': 'date-time',
           'title': 'Reference Date',
           'description': 'Timestamp of the spot price'
       },
       'subsystem': {
           'type': 'enum',
           'nullable': True,
           'description': 'Subsystem identifier',
           'enum_values': [
               'NORTE',
               'NORDESTE',
               'SUDESTE',
               'SUL',
               'SISTEMA INTERLIGADO NACIONAL'
           ]
       },
       'spot_price': {
           'type': 'number',
           'nullable': False,
           'title': 'Spot Price',
           'description': 'Spot price in R$/MWh'
       }
   }

get_table_columns()
~~~~~~~~~~~~~~~~~~~

Get a list of column names for a given table.

**Signature:**

.. code-block:: python

   def get_table_columns(table_name: str) -> list[str]

**Parameters:**

* ``table_name`` (str) - Table name in snake_case or PascalCase

**Returns:**

* ``list[str]`` - List of column names

**Example:**

.. code-block:: python

   columns = client.get_table_columns("ccee_spot_price")
   print(f"Columns: {columns}")
   # Output: ['id', 'reference_date', 'subsystem', 'spot_price', 'updated_at', ...]

Exceptions
----------

LakehouseError
~~~~~~~~~~~~~~

Base exception class for all PSR Lakehouse errors.

**Common Scenarios:**

* Invalid aggregation method specified
* Missing required parameters (e.g., ``group_by`` without ``aggregation_method``)
* API connection errors
* Authentication failures

**Example:**

.. code-block:: python

   from psr.lakehouse.exceptions import LakehouseError
   
   try:
       df = client.fetch_dataframe(
           table_name="ccee_spot_price",
           group_by=["subsystem"],
           # Missing aggregation_method - will raise LakehouseError
       )
   except LakehouseError as e:
       print(f"Error: {e}")

Best Practices
--------------

1. **Use Appropriate Method**
   
   * Use ``fetch_dataframe()`` for simple queries
   * Use ``fetch_dataframe_from_query()`` for complex queries with joins or advanced filtering

2. **Schema Discovery**
   
   * Always explore schema with ``get_schema()`` before querying unfamiliar tables
   * Use ``list_tables()`` to discover available data sources

3. **Date Filtering**
   
   * Always specify date ranges for large tables to avoid fetching excessive data
   * Use ISO format for dates: ``"2023-05-01"``

4. **Pagination**
   
   * The client automatically handles pagination
   * For very large datasets, consider breaking queries into smaller date ranges

5. **Error Handling**
   
   * Always wrap API calls in try-except blocks
   * Handle ``LakehouseError`` for application-specific errors

6. **Performance**
   
   * Use aggregation at the API level rather than fetching raw data
   * Specify only the columns you need in ``data_columns``
   * Use filters to reduce data transfer

Type Conversion
---------------

The client automatically handles type conversions:

* **Datetime columns**: Columns named ``reference_date`` are automatically converted to ``pd.Timestamp``
* **Index setting**: If ``reference_date`` exists, it's automatically set as the DataFrame index
* **Numeric types**: Numeric fields are preserved as appropriate pandas dtypes

Connection Management
---------------------

The HTTP connector uses lazy initialization - AWS credentials are only validated on the first API request. The singleton pattern ensures connection resources are reused throughout your application lifecycle.
