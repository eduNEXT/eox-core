========
EOX Core
========
|Maintainance Badge| |Test Badge| |PyPI Badge|

.. |Maintainance Badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
   :alt: Maintainance Status
.. |Test Badge| image:: https://img.shields.io/github/actions/workflow/status/edunext/eox-core/.github%2Fworkflows%2Ftests.yml?label=Test
   :alt: GitHub Actions Workflow Test Status
.. |PyPI Badge| image:: https://img.shields.io/pypi/v/eox-core?label=PyPI
   :alt: PyPI - Version

Eox-core is an `openedx plugin`_ for the `edx-platform`_, and part of the Edunext Open edX Extensions (aka EOX), that adds multiple API
endpoints to extend its functionality and avoid changing the base code directly. These
API endpoints include bulk creation of pre-activated users (for example, skip sending an activation email), enrollments, and pre-enrollment operations.

Installation
============

#. Add this plugin in your Tutor ``config.yml`` with the ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` setting.

   .. code-block:: yaml
      
      OPENEDX_EXTRA_PIP_REQUIREMENTS:
         - eox-core=={{version}} # basic installation
         - eox-core{{requirements}}=={{version}} # requeriments e.g. [sentry,tpa]. Useful for integration with third-party applications.
         
#. Save the configuration with ``tutor config save``.
#. Build an open edx image with ``tutor images build openedx``.
#. Launch your platform with ``tutor local launch``.

**Note:** To use all the features, you need to have `the tutor-forum plugin <https://github.com/overhangio/tutor-forum>`_ and `the eox-tenant plugin <https://github.com/eduNEXT/eox-tenant>`_.

Features
=========

- Support redirections with middleware.
- Add pipelines for authentication.
- Add a group of APIs.

  .. image:: docs/_images/eox-core-apis.png
      :alt: Eox-core APIs

Usage
=====

See the `How to section <https://github.com/eduNEXT/eox-core/tree/master/docs/how_to>`_ for guidance on middleware, pipeline and API usage.


Compatibility Notes
--------------------

+------------------+--------------+
| Open edX Release | Version      |
+==================+==============+
| Ironwood         | < 4.0        |
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
| Redwood          | >= 10.5.1    |
+------------------+--------------+

⚠️ The Maple version does not support Django 2.2 but it does support Django 3.2 as of eox-core 7.0.

The plugin is configured for the latest release (Redwood). The following changes in the plugin settings should be applied in order to be used for previous releases.

**Maple**

.. code-block:: yaml

   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_l_v1"

**Nutmeg**

.. code-block:: yaml

   EOX_CORE_PRE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1"
   EOX_CORE_ENROLLMENT_BACKEND: "eox_core.edxapp_wrapper.backends.enrollment_l_v1"

These settings can be changed in ``eox_core/settings/common.py`` or, in the instance settings.


🚨 If the release you are looking for is not listed, please note:

- If the Open edX release is compatible with the current eox-core version (see `Compatibility Notes <https://github.com/eduNEXT/eox-core?tab=readme-ov-file#compatibility-notes>`_), the default configuration is sufficient.
- If incompatible, you can refer to the README from the relevant version tag for configuration details (e.g., `v6.2.1 README <https://github.com/eduNEXT/eox-core/blob/v6.2.1/README.rst>`_).

Integrations with third-party services
--------------------------------------

The plugin offers some integrations listed below:

#. **Sentry**: This service allows tracking the errors generated on edx-platform. Check more details at https://sentry.io/welcome/.

   To enable the integration, follow the steps below:

   * Install the plugin with Sentry support (extras_require [sentry]).

   * Sign up/in your sentry account and create a new Django application integration.

   * Get the DSN for your integration. This is a unique identifier for your application.

   * Setup the following configuration values for edx-platform:

     .. code-block:: yaml

        EOX_CORE_SENTRY_INTEGRATION_DSN: <your DSN value>
        EOX_CORE_SENTRY_IGNORED_ERRORS: [] # optional
        EOX_CORE_SENTRY_EXTRA_OPTIONS: {} # optional

     - **EOX_CORE_SENTRY_INTEGRATION_DSN:** By default the setting is None, which disables the sentry integration.
     - **EOX_CORE_SENTRY_IGNORED_ERRORS:** List of the exceptions you want to ignore (see below for a reference).
     - **EOX_CORE_SENTRY_EXTRA_OPTIONS** Dictionary with extra options to be passed to the sentry client. For instance, it can be defined as:

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

Most views in eox-core use an auditing decorator, defined in our custom library, *eox-audit-model*,
that helps save relevant information about non-idempotent operations. By default, this functionality is turned on. To
check your auditing records go to Django sysadmin and find DJANGO EDUNEXT AUDIT MODEL.

You can check the `eox-audit-model`_ documentation for more information.

Development
===========

You can find more information about testing in the `Help for devs doc <https://github.com/eduNEXT/eox-core/blob/master/docs/help_for_devs/0001-include-test-cases-files.rst>`_.

.. _openedx plugin: https://github.com/openedx/edx-platform/tree/master/openedx/core/djangoapps/plugins
.. _edx-platform: https://github.com/openedx/edx-platform/
.. _eox-tenant: https://github.com/eduNEXT/eox-tenant/
.. _eox-audit-model: https://github.com/eduNEXT/eox-audit-model/

How to Contribute
=================

Contributions are welcome! See our `CONTRIBUTING`_ file for more
information – it also contains guidelines for how to maintain high code
quality, which will make your contribution more likely to be accepted.

.. _CONTRIBUTING: https://github.com/eduNEXT/eox-core/blob/master/CONTRIBUTING.rst


License
=======

This software is licensed under the terms of the AGPLv3. See the LICENSE file for details.
