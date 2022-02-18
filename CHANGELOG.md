# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/eduNEXT/eox-core/compare/v5.1.1...HEAD)

Please do not update the unreleased notes.

<!-- Content should be placed here -->
## [v5.1.1](https://github.com/eduNEXT/eox-core/compare/v5.1.0...v5.1.1) - 2022-01-17

### [5.1.1](https://github.com/eduNEXT/eox-core/compare/v5.1.0...v5.1.1) (2022-01-17)

### Added

- Add missing generate_password to the lilac users backend.

## [v5.1.0] - 2022-01-17

### Added

- Send post registration event during users registration through API.

## [v5.0.4] - 2022-01-04

### Changed

- Upgrade sentry-sdk to latest release (backward compatible with previews python versions).

## [v5.0.3] - 2021-11-10

### Added

- Add missing backend for Third Party Auth.

## [v5.0.2] - 2021-11-09

### Changed

- Separate eslint tests, so it doesn't block the PyPi release on CircleCi

## [v5.0.1] - 2021-11-08

### Changed

- Use the Lilac backends for the test settings. Previous Open edX releases test
- suites may not be compatible.

## [v5.0.0] - 2021-11-01

### Changed

- BREAKING CHANGE: Default backends for edxapp users, pre-enrollments and enrollments are not compatible with Juniper or older versions.

### Added

- Update Users backend for Lilac with Juniper backend.
- Openedx compatibility notes to readme.

## [v4.17.0] - 2021-10-21

### Added

- Date and time of enrolment creation to the Get CourseEnrollment endpoint.

## [v4.16.2] - 2021-09-30

### Changed

- Avoid failure when getting first_name from OIDC user details.

## [v4.16.1] - 2021-09-29

### Changed

- OIDC get_user_details method truncates user's first_name when exceeds max_length.

## [v4.16.0] - 2021-08-18

### Added

- Add new middleware to catch unhandled exceptions during the third party authentication.
- Add save_all_parameters argument to the eox-audit-model decorator for the Users API.
- Add filter_data list to the eox-audit-model decorator for the Enrollments API.

## [v4.15.1] - 2021-08-13

### Changed

- Add force flag to post method of enrollments api
- Update serializers used by enrollments api

## [v4.15.0] - 2021-08-06

### Changed

- Wrap course edxapp imports with try-except block.

### Added

- Course overview -edxapp model- function getter.

## [v4.14.0] - 2021-07-20

### Added

- Send post_register signal after user registration through API call.

## [v4.13.2] - 2021-07-16

### Changed

- EdxappExtendedUserSerializer to include all the custom registration fields.

## [v4.13.1] - 2021-07-15

### Changed

- New version of `edx-api-doc-tools` breaks Juniper, pin it to 1.4.0

## [v4.13.0] - 2021-07-12

### Added

- Add User API documentation.
- Allow profile fields to be included when creating a user.
- Add skip_password flag to omit password when creating a user if enabled.
- Allow user profile fields to be updated (update user endpoint).
- Allow searching by username when using the update user endpoint.

### Changed

- Move audit_wrapper to audit-model and rename it.
- Record sensitive data as hidden fields (eg. passwords)

## [v4.12.0] - 2021-06-29

### Changed

- Override the `get_user_id` method from `ConfigurableOpenIdConnectAuth` to include a slug before the uid.
- Add debug mode option to extra_data method from the ConfigurableOpenIdConnectAuth backend.

## [v4.11.0] - 2021-06-24

### Changed

- Add extra_data to ConfigurableOpenIdConnectAuth.

## [v4.10.2] - 2021-06-07

### Changed

- Update action names in EdxappPreEnrollment view.

## [v4.10.1] - 2021-06-03

### Added

- Add method override in ConfigurableOpenIdConnectAuth to avoid getting per class config.

## [v4.10.0] - 2021-05-28

### Added

- Decorate views that change or register some information.
- Include eox-audit-model wrapper.

## [v4.9.0] - 2021-05-12

- Add backends to fit lilac release.

## [v4.8.0] - 2021-04-29

- Add TPA pipeline steps to register signup sources.

## [v4.7.0] - 2021-03-25

- Add new endpoint to replace username.
- Add new endpoint to remove user.

## [v4.6.0] - 2021-03-08

- Add a new endoint to run celery taks

## [v4.5.1] - 2021-02-12

- Create a record in the UserAttribute table for each user with a password generated in the tpa pipeline.

## [v4.5.0] - 2021-02-10

### Added

- Add function that logs the information from the pipeline steps.

## [v4.4.1] - 2021-02-09

### Changed

- Pipeline step force_user_post_save_callback now sends the post_save signal if the user is new.

## [v4.4.0] - 2021-02-04

### Added

- Add new pipeline step to ensure creation of users with usable password

## [v4.3.0] - 2021-1-28

### Added

- Integration tests for the Grades API.

### Changed

- Integration tests now are only run if an environment variable `TEST_INTEGRATION` is set.
- Fix the parsing of optional parameters for the Grades API.

## [v4.2.0] - 2021-1-27

### Added

- New Grades API to retrieve grades from a single user on a course.
- Pipeline function to assert information returned by the TPA provider.

## [v4.1.0] - 2021-1-20

### Added

- Pipeline function to avoid disconnection from TPA provider.

## [v4.0.0] - 2021-1-14

### Added

- Add swagger support.
- Improve internal documentation for the Enrollment API.
- New suite of Enrollment integration tests.

### Changed

- BREAKING CHANGE: The requirements are not compatible with Ironwood anymore.

### Removed

- Support for Ironwood.

## [v3.4.0] - 2020-12-16

### Added

- Revert previous change in order to add EoxCoreAPIPermission to UserInfo APIView.

## [v3.3.0] - 2020-12-16

### Removed

- EoxCoreAPIPermission from UserInfo APIView

## [v3.2.0] - 2020-11-18

### Added

- Add support for django-filter versions superior to 2.0.0.
- Add support to enrollments API in Juniper.

## [v3.1.0] - 2020-10-20

### Added

- Add support for DOT clients in the EoxPermissions for API calls

### Changed

- Change how dependencies are specified to comply with OEP-18.

## [v3.0.0] - 2020-09-30

### Added

- Juniper support.
- Add proctoring test settings since this had the wrong proctoring version.
- Adding bearer_authentication to support django-oauth2-provider and django-oauth-toolkit

### Changed

- BREAKING CHANGE: Default backend for edxapp users now is not compatible with Ironwood. In order to use Ironwood, make sure that
- the Django setting EOX_CORE_USERS_BACKEND is equal to "eox_core.edxapp_wrapper.backends.users_h_v1".

### Removed

- Ironwood support.
- LoginFailures andUserSignupsource admin models.

## [v2.14.0] - 2020-09-09

### Added

- Add a new configurable view to update edxapp users.

## [v2.13.0] - 2020-06-17

### Added

- First release on PyPI.

## [v2.12.3] - 2020-05-06

### Added

- Improve the way that we can filter sentry exceptions.

## [v2.12.1] - 2020-04-16

### Added

- Add a completely configurable OpenId Connect based backend for third party auth.

## [v2.11.1] - 2020-04-15

### Added

- Use USERNAME_MAX_LENGTH defined in edx-platform.

## [v2.9.0] - 2020-04-06

### Added

- Add capability to ignore exceptions in sentry.

## [v2.8.0] - 2020-03-20

### Added

- Adding sentry integration

## [v2.6.0] - 2020-01-09

### Removed

- Remove microsite configuration mentions.

## [v0.14.0] - 2019-05-09

### Added

- Course management automation. This new Studio module allows you to make changes to the course configuration for several courses at once. More information: https://github.com/eduNEXT/eox-core#course-management-automation
- Linting tests: Now, pylint and eslint tests are running on CircleCI tests.
