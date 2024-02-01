=======================
EOX core |build-status|
=======================

.. |build-status| image:: https://circleci.com/gh/eduNEXT/eox-core.svg?style=svg

Eox-core (A.K.A. Edunext Open extensions) is an `openedx plugin`_, for the `edx-platform`_ that adds multiple API
endpoints in order to extend the functionality of the `edx-platform`_ and avoid changing the base code directly. These
API endpoints includes bulk creation of pre-activated users (for example, skip sending an activation email), enrollments
and pre-enrollment operations.

Installation
============

#. Add this plugin in your Tutor ``config.yml`` in the ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` variable.
#. Save your configuration with ``tutor config save``.
#. Build your open edx image with ``tutor images build openedx``.
#. Launch your platform with ``tutor local launch``.

**Note:** To use all the features, you need to have `the tutor-forum plugin <https://github.com/overhangio/tutor-forum>`_ and `the eox-tenant plugin <https://github.com/eduNEXT/eox-tenant>`_.

Features
=========
- Support redirections with middlewares.
- Add pipelines to be used with ``openedx-filters``.
- Add a group of APIs.

   .. image:: docs/_images/eox-core-apis.png
        :alt: Eox-core APIs

You can find more information in `Help for devs doc <https://github.com/eduNEXT/eox-core/blob/master/docs/help_for_devs/0001-include-test-cases-files.rst>`_.

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
| Palm             | >= 9.0       |
+------------------+--------------+
| Quince           | >= 10.0      |
+------------------+--------------+

**NOTE**: The Maple version does not support Django 2.2 but it does support Django 3.2 as of eox-core 7.0.

The following changes to the plugin settings are necessary. If the release you are looking for is
not listed, then the accumulation of changes from previous releases is enough.

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

**Olive, Palm and Quince**

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
        EOX_CORE_SENTRY_EXTRA_OPTIONS: {} # optional

     By default, **EOX_CORE_SENTRY_INTEGRATION_DSN** setting is None, which disables the sentry integration.
     **EOX_CORE_SENTRY_IGNORED_ERRORS** is optional. It is a list of the exceptions you want to ignore. For instance, it can be defined as:
     **EOX_CORE_SENTRY_EXTRA_OPTIONS** is optional. It is a dictionary with extra options to be passed to the sentry client. For instance, it can be defined as:

     .. code-block:: yaml

        EOX_CORE_SENTRY_IGNORED_ERRORS: [
          'xmodule.exceptions.NotFoundError',
          'openedx.core.djangoapps.user_authn.exceptions.AuthFailedError',
        ]
        EOX_CORE_SENTRY_EXTRA_OPTIONS:
            experiments: 
               profiles_sample_rate: 0.5
            another_client_parameter: 'value'


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
