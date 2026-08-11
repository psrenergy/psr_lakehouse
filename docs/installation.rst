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

Logging In
----------

The production lakehouse sits behind a load balancer that authenticates against PSR's Cognito
user pool, so a request without a session is answered with a redirect to the login page rather
than with data. Log in once from a terminal and the session is cached in
``~/.psr-lakehouse/session.json`` for later runs:

.. code-block:: bash

   psr-lakehouse login    # opens a browser to sign in
   psr-lakehouse whoami   # shows the cached session and when it expires
   psr-lakehouse logout   # forgets it

Signing in happens in the browser, so every method the user pool offers works: a password,
Google, a passkey, MFA. No credential is ever typed into the terminal.

How It Works, And Why The 401 Is Expected
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The flow is not quite the browser login you may be used to, for a reason worth knowing about.
The client has to *start* it, because the load balancer will only complete a sign-in for whoever
holds the ``AWSALBAuthNonce`` cookie it issues at the start — and that cookie is in the client,
not in the browser. If the browser were left to run the flow end to end, the browser would be
the one holding the session afterwards, which is no use to a Python process.

So after you sign in, the browser is left on a **401 Authorization Required** page. That is the
expected, successful outcome: the authorization code is sitting unspent in that page's URL. Copy
the URL back into the prompt and the client redeems the code itself, which is how the session
cookie ends up where the client can use it.

If the load balancer has already spent the code by then, the client says so and falls back to
asking for the ``AWSELBAuthSessionCookie-0`` value from the browser's developer tools, which
works in every case.

Scripts do not have to log in beforehand: the first request that comes back from the login page
starts the login and retries itself, so an interactive session recovers on its own.

.. code-block:: python

   from psr.lakehouse import login

   login()

For unattended runs — CI, a cron job, a container — there is no browser and nothing to paste
into, so there is no way to sign in from scratch. Log in once interactively and make the cached
session available to the job, pointing ``LAKEHOUSE_SESSION_FILE`` at it if it lives somewhere
other than ``~/.psr-lakehouse/session.json``. ``LAKEHOUSE_AUTO_LOGIN=0`` turns the automatic
login off entirely, so a missing session raises immediately instead of waiting on a prompt.

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
