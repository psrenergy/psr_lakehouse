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
       data_columns=["reference_date", "subsystem", "spot_price"],
       start_reference_date="2023-05-01",
       end_reference_date="2023-05-02",
   )
   print(df)

The result is a pandas DataFrame with the query results.

Checking Your Usage
~~~~~~~~~~~~~~~~~~~

Every plan has a weekly row quota. ``usage()`` shows your account, its plan,
the tables it can query and how much of the quota is left:

.. code-block:: python

   from psr.lakehouse import usage

   usage()

.. code-block:: text

   PSR Lakehouse
     Account   Jane Doe <jane.doe@email.com>
     Plan      Beta Tester
     API       https://api.example.com
     Tables    6 available from 2 sources
               CCEE 4, ONS 2
               client.list_tables() lists them all

   Limits
     Weekly rows  [███████░░░░░░░░░░░░░] 370 / 1,000 (37%)
                  630 left this week

If a query needs more rows than the quota has left, ``fetch_dataframe`` returns
the first rows that fit and prints a notice to stderr. The next query raises an
error that says when the quota frees.

Filtering Data
--------------

Filter by Column Values
~~~~~~~~~~~~~~~~~~~~~~~

Use the ``filters`` parameter to filter by exact column values:

.. code-block:: python

   # Filter by subsystem
   df = client.fetch_dataframe(
       table_name="ons_stored_energy_subsystem",
       data_columns=["reference_date", "subsystem", "max_stored_energy", "verified_stored_energy_percentage"],
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
       data_columns=["reference_date", "spot_price"],
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

Fetching Only What Changed
--------------------------

Data is revised after it is published. Instead of fetching a whole range again,
ask which days changed with ``last_updated()``. It returns one row per day with
the last time the day was written and how many rows it holds. Call it before
fetching the data, not after: a write landing in between would be in ``seen``
but not in your data, and would never be fetched again.

.. code-block:: python

   table = "ons_power_plant_hourly_generation"
   seen = client.last_updated(table, since="2025-10-01", until="2025-10-31")
   df = client.fetch_dataframe(table, start_reference_date="2025-10-01", end_reference_date="2025-10-31")

Keep ``seen`` next to the data (parquet keeps its types; read back from CSV the
merge below fails). Later, ask again: a day whose ``last_updated_at`` or ``rows``
differs, or that is new, has changed since. Fetch those days again, then keep the
new answer as ``seen``:

.. code-block:: python

   now = client.last_updated(table, since="2025-10-01", until="2025-10-31")
   changed = now.merge(seen, how="left", indicator=True).query("_merge == 'left_only'")["date"]
   for day in changed.dt.strftime("%Y-%m-%d"):
       day_df = client.fetch_dataframe(table, start_reference_date=day, end_reference_date=day)
       # replace that day in df with day_df
   seen = now

Each day returned counts as one row towards the weekly row quota.

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
