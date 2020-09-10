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

* Add proctoring test settings since this had the wrong proctoring version.

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
