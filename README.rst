=======================
EOX core |build-status|
=======================

.. |build-status| image:: https://circleci.com/gh/eduNEXT/eox-core.svg?style=svg

Eox-core (A.K.A. Edunext Open extensions) is an `openedx plugin`_, for the `edx-platform`_ that adds multiple API endpoints in order to extend the functionality of the `edx-platform`_ and avoid changing the base code directly. These API endpoints includes bulk creation of pre-activated users (for example, skip sending an activation email) and enrollments.

Usage
=====

1) Create the oauth client at http://localhost:18000/admin/oauth2/client/add/, copy the client-id and client-secret.

2) Generate an auth-token using that client-id and client-secret:

.. code-block:: bash

	$ curl -X POST -d "client_id=<YOUR_CLIENT_ID>&client_secret=<YOUR_CLIENT_SECRET>
		&grant_type=client_credentials" http://localhost:18000/oauth2/access_token/

3) Use the token to call the API as you need:

.. code-block:: bash

	# User creation API example
	curl -X POST --header "Authorization: Bearer <YOUR_AUTH_TOKEN>" -H "Accept: application/json" \
		http://localhost:18000/eox-core/api/v1/user/ --header "Content\-Type: application/json" \
		--data  '{"username": "jsmith", "email": "jhon@example.com", "password": "qwerty123",
		"fullname": "Jhon Smith"}'

	# Enroll api example
	curl -X POST --header "Authorization: Bearer <YOUR_AUTH_TOKEN>" -H "Accept: application/json" \
		http://localhost:18000/eox-core/api/v1/enrollment/ --header "Content-Type: application/json" \
		--data '{"course_id": "course-v1:edX+DemoX+Demo_Course", "email": "edx@example.com",
		"mode": "audit", "force": 1}'

Installation on Open edX Devstack
=================================
- Install the Ironwood version of the `Open edX devstack`_

- Clone the git repo:

.. code-block:: bash

	cd ~/Documents/eoxstack/src/  # Assuming that devstack is in  ~/Documents/eoxstack/devstack/
	sudo mkdir edxapp
	cd edxapp
	git clone git@github.com:eduNEXT/eox-core.git

- Install plugin from your server (in this case the devstack docker lms shell):

.. code-block:: bash

	cd ~/Documents/eoxstack/devstack  # Change for your devstack path (if you are using devstack)
	make lms-shell  # Enter the devstack machine (or server where lms process lives)
	sudo su edxapp -s /bin/bash  # if you are using devstack you need to use edxapp user
	source /edx/app/edxapp/venvs/edxapp/bin/activate
	cd /edx/src/edxapp/eox-core
	pip install -e .

Development
===========

To update dependencies you must edit the .in files (not requirements.txt directly) and compile them using pip-tools:

.. code-block:: bash

	$ source /path/to/venv/bin/activate
	(venv)$ pip install pip-tools
	(venv)$ pip-compile

Integrations with third party services
======================================

The plugin offers some integrations listed below:

#. **Sentry**: This service allows to track the errors generated on edx-platform. Check more details in https://sentry.io/welcome/. To enable the integration, follow the steps below:

  - Install the plugin with Sentry support (extras_require [sentry]).

  - Sign up/in to your sentry account and create a new Django application integration.

  - Get the DSN for your integration. This is an unique identifier for your application.

  - Setup the following configuration values for edx-platform:

    .. code-block:: yaml

      EOX_CORE_SENTRY_INTEGRATION_DSN: <your DSN value>
      EOX_CORE_SENTRY_IGNORED_ERRORS: [] # optional

 
    By default, **EOX_CORE_SENTRY_INTEGRATION_DSN** setting is None, which disables the sentry integration.
    **EOX_CORE_SENTRY_IGNORED_ERRORS** is optional. It is a list of the exceptions you want to ignore. For instance, it can be defined as:

    .. code-block:: yaml

      EOX_CORE_SENTRY_IGNORED_ERRORS: [
        'xmodule.exceptions.NotFoundError',
        'openedx.core.djangoapps.user_authn.exceptions.AuthFailedError',
      ]

Course Management automation
============================

This component allows Studio users to make changes in multiple courses, such as:

* Add or remove staff/instructor users across multiple courses in one organization.
* Change course settings in multiple courses at once.
* Re-run a course across multiple organizations.

Compilation
###########

We use webpack to bundle the React js application and its dependencies.
To compile in a development environment, run this command on the root folder:

npm run build-dev

Otherwise, if you want to compile for use in production environment, run this command instead:

npm run build-prod

These commands are defined in the package.json file and each one exports two bundle files (build.js and course-management.bundle.css) inside of eox_core/static folder.

EOX core migration notes
========================

**Migrating to version 2.0.0**

From version **2.0.0**, middlewares **RedirectionsMiddleware** and **PathRedirectionMiddleware** are now included in this plugin. These middlewares were moved from the **`eox-tenant`_** plugin.

if you installed **eox-core** alongside **eox-tenant** plugin, follow the steps below:

- Upgrade eox-tenant to version **1.0.0** (previous releases are not compatible with eox-core 2.0.0)
- Run the plugin migrations as indicated below:

.. code-block:: bash

   $ python manage.py lms migrate eox_tenant --settings=<your app settings>
   $ python manage.py lms migrate eox_core --fake-initial --settings=<your app settings>

In case eox-tenant is not installed on the platform, just run the eox-core migrations.


.. _Open edX Devstack: https://github.com/edx/devstack/
.. _openedx plugin: https://github.com/edx/edx-platform/tree/master/openedx/core/djangoapps/plugins
.. _edx-platform: https://github.com/edx/edx-platform/
.. _eox-tenant: https://github.com/eduNEXT/eox-tenant/
