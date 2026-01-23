Advanced Examples
=================

This page contains advanced examples based on real-world usage patterns.

Example 1: Power Plant Generation Analysis
-------------------------------------------

Aggregate Generation by Plant Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to aggregate hourly generation data by plant type:

.. code-block:: python

   from psr.lakehouse import client

   df_generation = client.fetch_dataframe_from_query({
       "query_data": [
           "ONSPowerPlantHourlyGeneration.plant_type",
           "ONSPowerPlantHourlyGeneration.generation"
       ],
       "group_by": {
           "group_by_clause": [
               "ONSPowerPlantHourlyGeneration.plant_type"
           ],
           "default_aggregation_method": "sum"
       },
       "query_filters": [
           {
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "operator": ">=",
               "value": "2025-01-01"
           },
           {   
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "operator": "<=",
               "value": "2025-01-31"
           }     
       ]
   })

Daily Generation with Datetime Granularity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aggregate hourly data to daily granularity:

.. code-block:: python

   df_generation = client.fetch_dataframe_from_query({
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
           },
           {
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "operator": "<=",
               "value": "2025-01-31"
           }
       ]
   })

Hourly Data with Sorting
~~~~~~~~~~~~~~~~~~~~~~~~~

Fetch hourly generation data with custom ordering:

.. code-block:: python

   df_generation = client.fetch_dataframe_from_query({
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
           "datetime_granularity": "hour"
       },
       "order_by": [
           {
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "direction": "desc"
           },
           {
               "column": "ONSPowerPlantHourlyGeneration.plant_type",
               "direction": "asc"
           }
       ],
       "query_filters": [
           {
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "operator": ">=",
               "value": "2025-01-01"
           },
           {
               "column": "ONSPowerPlantHourlyGeneration.reference_date",
               "operator": "<=",
               "value": "2025-01-31"
           }
       ]
   })

Example 2: Joining Multiple Tables
-----------------------------------

Energy Load and Inflow Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates joining energy load data with inflow energy data:

.. code-block:: python

   df_energy_load = client.fetch_dataframe_from_query({
       "query_data": [
           "ONSEnergyLoadDaily.reference_date",
           "ONSEnergyLoadDaily.subsystem",
           "ONSEnergyLoadDaily.energy_load",
           "ONSInflowEnergySubsystem.gross_inflow_energy_mwavg",
           "ONSInflowEnergySubsystem.subsystem"
       ],
       "joins": [
           {
               "join_model": "ONSInflowEnergySubsystem",
               "join_filters": [
                   {
                       "column": "ONSEnergyLoadDaily.reference_date",
                       "value": "ONSInflowEnergySubsystem.reference_date",
                       "operator": "="
                   },
                   {
                       "column": "ONSEnergyLoadDaily.subsystem",
                       "value": "ONSInflowEnergySubsystem.subsystem",
                       "operator": "="
                   }
               ],
               "is_outer_join": False
           }
       ],
       "query_filters": [
           {
               "column": "ONSEnergyLoadDaily.reference_date",
               "operator": ">=",
               "value": "2025-01-01"
           },
           {
               "column": "ONSEnergyLoadDaily.reference_date",
               "operator": "<=",
               "value": "2025-01-31"
           }
       ]
   })

This creates an inner join between the two tables on both reference date and subsystem.

Example 3: Using the Simplified Interface
------------------------------------------

Alternative Method for Common Use Cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For simpler queries, you can use the ``fetch_dataframe`` method:

.. code-block:: python

   df_generation = client.fetch_dataframe(
       table_name="ons_power_plant_hourly_generation",
       data_columns=["plant_type", "generation"],
       start_reference_date="2025-01-01",
       end_reference_date="2025-01-31",
       group_by=["plant_type"],
       aggregation_method="sum"
   )

This is equivalent to the more verbose ``fetch_dataframe_from_query`` but simpler for basic use cases.

Example 4: Schema Exploration
------------------------------

Discovering Available Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from psr.lakehouse import client

   # List all available tables
   tables = client.list_tables()
   print(f"Available tables: {len(tables)}")
   print(tables[:10])  # Show first 10

   # Examine a specific table's schema
   table_name = "ccee_spot_price"
   schema = client.get_schema(table_name)
   
   # Display schema information
   for field_name, field_info in schema.items():
       print(f"\nField: {field_name}")
       print(f"  Type: {field_info.get('type')}")
       print(f"  Nullable: {field_info.get('nullable')}")
       
       if 'description' in field_info:
           print(f"  Description: {field_info['description']}")
       
       if 'enum_values' in field_info:
           print(f"  Allowed values: {field_info['enum_values']}")

Query Structure Reference
-------------------------

Understanding the Query Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``fetch_dataframe_from_query`` method accepts a dictionary with the following structure:

**Basic Structure:**

.. code-block:: python

   {
       "query_data": [
           "ModelName.column1",
           "ModelName.column2"
       ],
       "query_filters": [
           {
               "column": "ModelName.column_name",
               "operator": ">=",  # or "<=", "=", "!=", ">", "<"
               "value": "value"
           }
       ],
       "group_by": {
           "group_by_clause": ["ModelName.column1"],
           "default_aggregation_method": "sum",  # or "avg", "min", "max"
           "datetime_granularity": "day"  # or "hour", "week", "month"
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
               "is_outer_join": False  # or True for outer join
           }
       ]
   }

.. note::
   All fields are optional except ``query_data``. Model names use PascalCase (e.g., ``ONSPowerPlantHourlyGeneration``).
