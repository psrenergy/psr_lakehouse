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
* boto3
* requests-aws4auth

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The library requires configuration via environment variables:

**API URL** (required):

.. code-block:: bash

   LAKEHOUSE_API_URL="https://api.example.com"

**AWS Credentials** (for IAM authentication):

.. code-block:: bash

   AWS_ACCESS_KEY_ID="your-access-key"
   AWS_SECRET_ACCESS_KEY="your-secret-key"
   AWS_DEFAULT_REGION="us-east-1"

Programmatic Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can configure the client programmatically:

.. code-block:: python

   from psr.lakehouse import initialize

   initialize(
       base_url="https://api.example.com",
       aws_access_key_id="your-access-key",
       aws_secret_access_key="your-secret-key",
       region="us-east-1",
   )

.. note::
   The connector uses lazy initialization - credentials are only validated when making the first API request.

Authentication
--------------

PSR Lakehouse uses AWS Signature Version 4 (SigV4) for authenticating requests to AWS API Gateway endpoints. The library automatically handles:

* AWS credential resolution from environment or programmatic configuration
* Request signing using AWS4Auth
* Credential caching via singleton pattern

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
