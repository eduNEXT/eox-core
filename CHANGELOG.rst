Change Log
==========

..
   All enhancements and patches to eox-core will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).
.. There should always be an "Unreleased" section for changes pending release.
Unreleased
----------
Added
~~~~~~~
* Allow profile fields to be included when creating a user.
* Add skip_password flag to omit password when creating a user if enabled.
* Allow user profile fields to be updated (update user endpoint).
* Allow searching by username when using the update user endpoint.

Changed
~~~~~~~
* Move audit_wrapper to audit-model and rename it.
* Record sensitive data as hidden fields (eg. passwords)

[4.12.0] - 2021-06-29
---------------------
Changed
~~~~~~~
* Override the ``get_user_id`` method from ``ConfigurableOpenIdConnectAuth`` to
  include a slug before the uid.
* Add debug mode option to extra_data method from the ConfigurableOpenIdConnectAuth backend.

[4.11.0] - 2021-06-24
---------------------

Changed
~~~~~~~
* Add extra_data to ConfigurableOpenIdConnectAuth.

[4.10.2] - 2021-06-07
---------------------

Changed
~~~~~~~
* Update action names in EdxappPreEnrollment view.

[4.10.1] - 2021-06-03
--------------------
* Add method override in ConfigurableOpenIdConnectAuth to avoid getting per class
  config.

[4.10.0] - 2021-05-28
--------------------

Added
~~~~~
* Decorate views that change or register some information.
* Include eox-audit-model wrapper.

[4.9.0] - 2021-05-12
--------------------
* Add backends to fit lilac release.

[4.8.0] - 2021-04-29
--------------------
* Add TPA pipeline steps to register signup sources.

[4.7.0] - 2021-03-25
--------------------
* Add new endpoint to replace username.
* Add new endpoint to remove user.

[4.6.0] - 2021-03-08
--------------------
* Add a new endoint to run celery taks

[4.5.1] - 2021-02-12
--------------------
* Create a record in the UserAttribute table for each user with a password generated in the
  tpa pipeline.

[4.5.0] - 2021-02-10
--------------------
Added
~~~~~
* Added function that logs the information from the pipeline steps.

[4.4.1] - 2021-02-09
--------------------
Changed
~~~~~~~
* Pipeline step force_user_post_save_callback now sends the post_save signal if the user is new.

[4.4.0] - 2021-02-04
--------------------
Added
~~~~~
* Added a new pipeline step to ensure creation of users with usable password

[4.3.0] - 2021-1-28
--------------------
Added
~~~~~
* Integration tests for the Grades API.

Changed
~~~~~~
* Integration tests now are only run if an environment variable
  ``TEST_INTEGRATION`` is set.
* Fix the parsing of optional parameters for the Grades API.

[4.2.0] - 2021-1-27
--------------------
Added
~~~~~
* New Grades API to retrieve grades from a single user on a course.
* Pipeline function to assert information returned by the TPA provider.

[4.1.0] - 2021-1-20
--------------------
Added
~~~~~
* Pipeline function to avoid disconnection from TPA provider.


[4.0.0] - 2021-1-14
--------------------

Added
~~~~~
* Add swagger support.
* Improve internal documentation for the Enrollment API.
* New suite of Enrollment integration tests.

Changed
~~~~~~~
* **BREAKING CHANGE**: The requirements are not compatible with Ironwood anymore.".

Removed
~~~~~~~
* Support for Ironwood.

[3.4.0] - 2020-12-16
--------------------

Added
~~~~~
* Revert previous change in order to add EoxCoreAPIPermission to UserInfo APIView.

[3.3.0] - 2020-12-16
--------------------

Removed
~~~~~~~
* EoxCoreAPIPermission from UserInfo APIView

[3.2.0] - 2020-11-18
--------------------

Added
~~~~~
* Add support for django-filter versions superior to 2.0.0.
* Add support to enrollments API in Juniper.

[3.1.0] - 2020-10-20
--------------------

Added
~~~~~
* Add support for DOT clients in the EoxPermissions for API calls

Changed
~~~~~~~
* Change how dependencies are specified to comply with OEP-18.

[3.0.0] - 2020-09-30
---------------------

Added
~~~~~
* Juniper support.
* Add proctoring test settings since this had the wrong proctoring version.
* Adding bearer_authentication to support django-oauth2-provider and django-oauth-toolkit

Changed
~~~~~~~
* **BREAKING CHANGE**: Default backend for edxapp users now is not compatible with Ironwood. In order to use Ironwood, make sure that
  the Django setting EOX_CORE_USERS_BACKEND is equal to "eox_core.edxapp_wrapper.backends.users_h_v1".

Removed
~~~~~~~
* Ironwood support.
* LoginFailures andUserSignupsource admin models.

[2.14.0] - 2020-09-09
---------------------

Added
~~~~~

* Added a new configurable view to update edxapp users.

[2.13.0] - 2020-06-17
---------------------

Added
~~~~~

* First release on PyPI.

[2.12.3] - 2020-05-06
---------------------

Added
~~~~~

* Improve the way that we can filter sentry exceptions.

[2.12.1] - 2020-04-16
---------------------

Added
~~~~~

* Added a completely configurable OpenId Connect based backend for third party auth.

[2.11.1] - 2020-04-15
---------------------

Added
~~~~~

* Use USERNAME_MAX_LENGTH defined in edx-platform.

[2.9.0] - 2020-04-06
--------------------

Added
~~~~~

* Add capability to ignore exceptions in sentry.

[2.8.0] - 2020-03-20
--------------------

Added
~~~~~

* Adding sentry integration

[2.6.0] - 2020-01-09
--------------------

Removed
~~~~~~~

* Remove microsite configuration mentions.

[0.14.0] - 2019-05-09
---------------------

Added
~~~~~

* Course management automation. This new Studio module allows you to make changes to the course configuration for several courses at once. More information: https://github.com/eduNEXT/eox-core#course-management-automation
* Linting tests: Now, pylint and eslint tests are running on CircleCI tests.
