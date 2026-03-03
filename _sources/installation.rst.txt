Installation & Configuration
=============================

Installation
------------

Install PSR Lakehouse using pip:

.. code-block:: bash

   pip install psr-lakehouse

Requirements
------------

* Python 3.13+
* pandas
* requests

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The library requires configuration via environment variables:

**API URL** (required):

.. code-block:: bash

   LAKEHOUSE_API_URL="https://api.example.com"

Programmatic Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can configure the client programmatically:

.. code-block:: python

   from psr.lakehouse import initialize

   initialize(
       base_url="https://api.example.com",
   )

.. note::
   The connector validates connectivity during initialization by performing a health check against the API.

Development Setup
-----------------

For development, the project uses ``uv`` as the package manager:

.. code-block:: bash

   # Install dependencies
   uv sync

   # Build the package
   uv build

   # Run tests
   make test

   # Run linting and formatting
   make lint
