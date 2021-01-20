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

[4.0.0] - 2021-1-20
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
