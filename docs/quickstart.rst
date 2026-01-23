Quick Start Guide
=================

This guide will help you get started with PSR Lakehouse client.

Basic Usage
-----------

Import and Fetch Data
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from psr.lakehouse import client

   # Fetch CCEE spot price data
   df = client.fetch_dataframe(
       table_name="ccee_spot_price",
       indices_columns=["reference_date", "subsystem"],
       data_columns=["spot_price"],
       start_reference_date="2023-05-01",
       end_reference_date="2023-05-02",
   )
   print(df)

The result is a pandas DataFrame with a MultiIndex based on ``indices_columns``.

Filtering Data
--------------

Filter by Column Values
~~~~~~~~~~~~~~~~~~~~~~~

Use the ``filters`` parameter to filter by exact column values:

.. code-block:: python

   # Filter by subsystem
   df = client.fetch_dataframe(
       table_name="ons_stored_energy_subsystem",
       indices_columns=["reference_date", "subsystem"],
       data_columns=["max_stored_energy", "verified_stored_energy_percentage"],
       start_reference_date="2023-05-01",
       end_reference_date="2023-05-02",
       filters={"subsystem": "SOUTHEAST"},
   )

Date Range Filtering
~~~~~~~~~~~~~~~~~~~~

Use ``start_reference_date`` and ``end_reference_date`` to filter data by date:

.. code-block:: python

   df = client.fetch_dataframe(
       table_name="ccee_spot_price",
       indices_columns=["reference_date"],
       data_columns=["spot_price"],
       start_reference_date="2023-01-01",  # inclusive
       end_reference_date="2023-02-01",     # exclusive
   )

Aggregating Data
----------------

Group and Aggregate
~~~~~~~~~~~~~~~~~~~

Use ``group_by`` and ``aggregation_method`` to aggregate data:

.. code-block:: python

   # Group by subsystem and calculate average spot price
   df = client.fetch_dataframe(
       table_name="ccee_spot_price",
       indices_columns=["reference_date", "subsystem"],
       data_columns=["spot_price"],
       start_reference_date="2023-01-01",
       end_reference_date="2023-02-01",
       group_by=["subsystem"],
       aggregation_method="avg",
   )

Available aggregation methods:

* ``sum`` - Sum of values
* ``avg`` - Average of values
* ``min`` - Minimum value
* ``max`` - Maximum value

Temporal Aggregation
~~~~~~~~~~~~~~~~~~~~

Use ``datetime_granularity`` to aggregate datetime data to a coarser granularity:

.. code-block:: python

   # Aggregate hourly data to daily
   df = client.fetch_dataframe(
       table_name="ons_power_plant_hourly_generation",
       data_columns=["plant_type", "generation"],
       start_reference_date="2025-01-01",
       end_reference_date="2025-01-31",
       group_by=["reference_date", "plant_type"],
       aggregation_method="sum",
       datetime_granularity="day",  # Options: hour, day, week, month
   )

Ordering Results
----------------

Sort By Multiple Columns
~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``order_by`` parameter to sort results:

.. code-block:: python

   df = client.fetch_dataframe(
       table_name="ons_power_plant_hourly_generation",
       data_columns=["plant_type", "generation"],
       group_by=["reference_date", "plant_type"],
       aggregation_method="sum",
       datetime_granularity="day",
       order_by=[
           {"column": "reference_date", "direction": "desc"},
           {"column": "plant_type", "direction": "asc"},
       ],
   )

Schema Discovery
----------------

List Available Tables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tables = client.list_tables()
   print(tables)
   # Output: ['CCEESpotPrice', 'ONSEnergyLoadDaily', 'ONSStoredEnergySubsystem', ...]

Get Table Schema
~~~~~~~~~~~~~~~~

Retrieve detailed schema information including field types, descriptions, and allowed values:

.. code-block:: python

   schema = client.get_schema("ccee_spot_price")
   print(schema)

Example schema output:

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
           'enum_values': ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
       },
       'spot_price': {
           'type': 'number',
           'nullable': False,
           'title': 'Spot Price',
           'description': 'Spot price in R$/MWh'
       }
   }

Next Steps
----------

* Check out the :doc:`examples` page for more advanced use cases
* Read the :doc:`api` reference for complete method documentation
* Explore available tables using ``client.list_tables()``
