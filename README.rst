=======================
EOX core |build-status|
=======================

.. |build-status| image:: https://circleci.com/gh/eduNEXT/eox-core.svg?style=svg

Eox-core (A.K.A. Edunext Open extensions) is an `openedx plugin`_, for the `edx-platform`_ that adds multiple API
endpoints in order to extend the functionality of the `edx-platform`_ and avoid changing the base code directly. These
API endpoints includes bulk creation of pre-activated users (for example, skip sending an activation email), enrollments
and pre-enrollment operations.

Usage
=====

Open edX releases before juniper
--------------------------------

#. Create the oauth client at http://localhost:18000/admin/oauth2/client/add/, copy the client-id and client-secret.

#. Generate an auth-token using that client-id and client-secret:

   .. code-block:: bash

      $ curl -X POST -d "client_id=<YOUR_CLIENT_ID>&client_secret=<YOUR_CLIENT_SECRET> &grant_type=client_credentials" http://localhost:18000/oauth2/access_token/

#. Use the token to call the API as you need:

   * User creation API example

     .. code-block:: bash
     
        curl -X POST http://localhost:18000/eox-core/api/v1/user/ \
             -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
             -H "Accept: application/json" \
             -H "Content\-Type: application/json" \
        	   --data  '{"username": "jsmith", "email": "jhon@example.com", "password": "qwerty123", "fullname": "Jhon Smith"}'

   * Enroll api example

     .. code-block:: bash

        curl -X POST http://localhost:18000/eox-core/api/v1/enrollment/ \
              -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
              -H "Accept: application/json" \
              -H "Content\-Type: application/json" \
         	   --data '{"course_id": "course-v1:edX+DemoX+Demo_Course", "email": "edx@example.com", "mode": "audit", "force": 1}'


Open edX releases after juniper
-------------------------------

Instead of step 1, follow:

#. Create a Django Oauth Toolkit Application at http://localhost:18000/admin/oauth2_provider/application/add/,
   copy the client-id and client-secret. Then follow 2 and 3.


Installation on Open edX Devstack
=================================

* Install either the Ironwood or Juniper version of the `Open edX devstack`_

* Clone the git repo:

  .. code-block:: bash
  
     cd ~/Documents/eoxstack/src/  # Assuming that devstack is in  ~/Documents/eoxstack/devstack/
     sudo mkdir edxapp
     cd edxapp
     git clone git@github.com:eduNEXT/eox-core.git

- Install plugin from your server (in this case the devstack docker lms shell):

  .. code-block:: bash
  
     cd ~/Documents/eoxstack/devstack  # Change for your devstack path (if you are using devstack)
     make lms-shell  # Enter the devstack machine (or server where lms process lives)
     cd /edx/src/edxapp/eox-core
     pip install -e .

Compatibility Notes
--------------------

+------------------+--------------+
| Open edX Release | Version      |
+==================+==============+
| Ironwood         | < 3.0        |
+------------------+--------------+
| Juniper          | >= 3.0 < 5.0 |
+------------------+--------------+
| Koa              | >= 4.9 < 6.0 |
+------------------+--------------+
| Lilac            | >= 4.9 < 6.0 |
+------------------+--------------+
| Maple            | >= 6.0       |
+------------------+--------------+
| Nutmeg           | >= 7.0       |
+------------------+--------------+
| Olive            | >= 8.0       |
+------------------+--------------+

**NOTE**: The Maple version does not support Django 2.2 but it does support Django 3.2 as of eox-core 7.0.

The following changes to the plugin settings are necessary. If the release you are looking for is
not listed, then the accumulation of changes from previous releases is enough.

**Ironwood**

.. code-block:: yaml

   EOX_CORE_USERS_BACKEND: "eox_core.edxapp_wrapper.backends.users_h_v1"
   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_h_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_h_v1"

**Juniper**

.. code-block:: yaml

   EOX_CORE_USERS_BACKEND: "eox_core.edxapp_wrapper.backends.users_j_v1"
   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_h_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_h_v1"

**Koa**

.. code-block:: yaml

   EOX_CORE_USERS_BACKEND: "eox_core.edxapp_wrapper.backends.users_l_v1"
   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_l_v1"

**Lilac**

.. code-block:: yaml

   EOX_CORE_USERS_BACKEND: "eox_core.edxapp_wrapper.backends.users_l_v1"
   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_l_v1"

**Maple**

.. code-block:: yaml

   EOX_CORE_USERS_BACKEND: "eox_core.edxapp_wrapper.backends.users_m_v1"
   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_l_v1"

**Nutmeg**

.. code-block:: yaml

   EOX_CORE_USERS_BACKEND: "eox_core.edxapp_wrapper.backends.users_m_v1"
   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_l_v1"

**Olive**

.. code-block:: yaml

   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_o_v1"

These settings can be changed in ``eox_core/settings/common.py`` or, for example, in ansible configurations.

**NOTE**: the current ``common.py`` works with Open edX Nutmeg version.


Dependency Management
=====================

EOX core now follows OEP-18 so the correct way to update dependencies is to run ``make upgrade`` inside your virtualenv.


Integrations with third party services
======================================

The plugin offers some integrations listed below:

#. **Sentry**: This service allows to track the errors generated on edx-platform. Check more details in https://sentry.io/welcome/.
   To enable the integration, follow the steps below:

   * Install the plugin with Sentry support (extras_require [sentry]).

   * Sign up/in to your sentry account and create a new Django application integration.

   * Get the DSN for your integration. This is an unique identifier for your application.

   * Setup the following configuration values for edx-platform:

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

EOX core migration notes
========================

**Migrating to version 2.0.0**

From version **2.0.0**, middlewares **RedirectionsMiddleware** and **PathRedirectionMiddleware** are now included in
this plugin. These middlewares were moved from the **`eox-tenant`_** plugin.

if you installed **eox-core** alongside **eox-tenant** plugin, follow the steps below:

- Upgrade eox-tenant to version **1.0.0** (previous releases are not compatible with eox-core 2.0.0)
- Run the plugin migrations as indicated below:

.. code-block:: bash

   $ python manage.py lms migrate eox_tenant --settings=<your app settings>
   $ python manage.py lms migrate eox_core --fake-initial --settings=<your app settings>

In case eox-tenant is not installed on the platform, just run the eox-core migrations.


Auditing Django views
=====================

The majority of views in eox-core use an auditing decorator, defined in our custom library called `eox-audit-model`_,
that helps saving relevant information about non-idempotent operations. By default this functionality is turned on. To
check your auditing records go to Django sysadmin and find DJANGO EDUNEXT AUDIT MODEL.

For more information, check the eox-audit-model documentation.


.. _Open edX Devstack: https://github.com/edx/devstack/
.. _openedx plugin: https://github.com/edx/edx-platform/tree/master/openedx/core/djangoapps/plugins
.. _edx-platform: https://github.com/edx/edx-platform/
.. _eox-tenant: https://github.com/eduNEXT/eox-tenant/
.. _eox-audit-model: https://github.com/eduNEXT/eox-audit-model/

How to Contribute
-----------------

Contributions are welcome! See our `CONTRIBUTING`_ file for more
information – it also contains guidelines for how to maintain high code
quality, which will make your contribution more likely to be accepted.

.. _CONTRIBUTING: https://github.com/eduNEXT/eox-core/blob/master/CONTRIBUTING.rst
