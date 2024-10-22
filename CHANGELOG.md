# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/eduNEXT/eox-core/compare/v11.0.0...HEAD)

Please do not update the unreleased notes.

<!-- Content should be placed here -->

## [v11.0.0](https://github.com/eduNEXT/eox-core/compare/v10.6.0...v11.0.0) - (2024-10-22)

#### ⚠ BREAKING CHANGES

- **Dropped Support for Django 3.2**: Removed support for Django 3.2 in this plugin. As a result, we have also dropped support for Open edX releases from Maple up to and including Palm, which rely on Django 3.2. Future versions of this plugin may not be compatible with these Open edX releases.

## [v10.6.0](https://github.com/eduNEXT/eox-core/compare/v10.5.1...v10.6.0) - (2024-09-17)

### Added

- **Integration Tests**: A new set of integration tests was added to validate
  the Users API. These tests ensure the correct behavior of endpoints
  interacting with Open edX components.

### Changed

- **Unit Tests**: The unit tests were moved to a new directory, `/unit`, to
  separate them from the integration tests. This change aims to improve the
  organization of the tests and make it easier to identify the different types
  of tests.

## [v10.5.1](https://github.com/eduNEXT/eox-core/compare/v10.5.0...v10.5.1) - (2024-07-19)

### Fixed

- **Redwood Compatibility**: Corrected a build-time error, ensuring full
  compatibility with the Redwood release. For this, a new `ImproperlyConfigured`
  exception is handled when loading the API permissions.

### Changed

- **Improve Documentation**: Update the README to include a more detailed
  description of the project and its features. A new how-to section was
  included with information about API, Middlewares, and pipelines.

## [v10.5.0](https://github.com/eduNEXT/eox-core/compare/v10.4.0...v10.5.0) - (2024-07-08)

### Added

- **Integration Tests**: A new GitHub workflow has been added to run
  integration tests. These tests validate backend imports and ensure
  the `/eox-info` endpoint functions correctly.

### Changed

- **Redwood Support**: Upgrade requirements base on edx-platform Redwood
  release, update GitHub workflows with new actions version, and update
  integration test to use new Redwood release with Tutor.

## [v10.4.0](https://github.com/eduNEXT/eox-core/compare/v10.3.0...v10.4.0) - 2024-05-24

### [10.4.0](https://github.com/eduNEXT/eox-core/compare/v10.3.0...v10.4.0) (2024-05-24)

#### Features

* add integration test file ([#267](https://github.com/eduNEXT/eox-core/issues/267)) ([beddb10](https://github.com/eduNEXT/eox-core/commit/beddb10b7d137732769c0a3557e104ca3ddf7905))

## [v10.3.0](https://github.com/eduNEXT/eox-core/compare/v10.2.0...v10.3.0) - 2024-05-23

### [10.3.0](https://github.com/eduNEXT/eox-core/compare/v10.2.0...v10.3.0) (2024-05-23)

#### Features

* add user lang cookie preference ([#265](https://github.com/eduNEXT/eox-core/issues/265)) ([5dec49b](https://github.com/eduNEXT/eox-core/commit/5dec49b14a819de298f74a0134302dd46ff2137d))

## [v10.2.0](https://github.com/eduNEXT/eox-core/compare/v10.1.0...v10.2.0) - 2024-05-17

### [10.2.0](https://github.com/eduNEXT/eox-core/compare/v10.1.0...v10.2.0) (2024-05-17)

#### Features

* added logs to errors imports ([#259](https://github.com/eduNEXT/eox-core/issues/259)) ([50cb82e](https://github.com/eduNEXT/eox-core/commit/50cb82e07c0f25f8b45c6ed672cbc790e0862a26))

## [v10.1.0](https://github.com/eduNEXT/eox-core/compare/v10.0.0...v10.1.0) - 2024-03-19

### [10.1.0](https://github.com/eduNEXT/eox-core/compare/v10.0.0...v10.1.0) (2024-03-19)

#### Features

* add workflow to add items to the Dedalo project DS-831 ([#264](https://github.com/eduNEXT/eox-core/issues/264)) ([c2d6116](https://github.com/eduNEXT/eox-core/commit/c2d6116f75faa00a7a98fea071c9aeaa664803f9))

## [v10.0.0](https://github.com/eduNEXT/eox-core/compare/v9.1.1...v10.0.0) - 2024-02-01

### [10.0.0](https://github.com/eduNEXT/eox-core/compare/v9.1.1...v10.0.0) (2024-02-01)

#### ⚠ BREAKING CHANGES

* add compatibility with quince release
  
* chore: update constraints & upgrade requirements
  
* fix: was mandatory to send any get_response
  
* chore: update github-actions
  
* chore: install test dependencies as dev ones
  
* docs: update README for showing quince support
  
* fix: malformed table
  

#### Performance Improvements

* add support with Quince release ([#262](https://github.com/eduNEXT/eox-core/issues/262)) ([7186a13](https://github.com/eduNEXT/eox-core/commit/7186a136ea35d24027b7d974f34777af829e7108))

## [v9.1.1](https://github.com/eduNEXT/eox-core/compare/v9.1.0...v9.1.1) - 2024-01-25

### [9.1.1](https://github.com/eduNEXT/eox-core/compare/v9.1.0...v9.1.1) (2024-01-25)

### Bug Fixes

* update urls in favor of re_path for deprecation ([#260](https://github.com/eduNEXT/eox-core/issues/260)) ([bb15fcc](https://github.com/eduNEXT/eox-core/commit/bb15fccfa437b7e537d9eae7a725794d1945b659))

## [v9.1.0](https://github.com/eduNEXT/eox-core/compare/v9.0.0...v9.1.0) - 2024-01-12

### [9.1.0](https://github.com/eduNEXT/eox-core/compare/v9.0.0...v9.1.0) (2024-01-12)

#### Features

* enable custom_reg_form capability ([#256](https://github.com/eduNEXT/eox-core/issues/256)) ([05f2756](https://github.com/eduNEXT/eox-core/commit/05f2756ce074abadef648f6a55311e1be2eaeff8))

## [v9.0.0](https://github.com/eduNEXT/eox-core/compare/v8.2.0...v9.0.0) - 2023-11-30

### [9.0.0](https://github.com/eduNEXT/eox-core/compare/v8.2.0...v9.0.0) (2023-11-30)

#### ⚠ BREAKING CHANGES

* remove openedx-events constraint to use what's installed (#252)
  
* add compatibility with palm
  
* ci: update workflow versions
  
* chore: update constraints
  
* chore: update requirements
  
* fix: remove python 3.10 because it causes an error in the build created by backports-zoneinfo
  
* fix: add and avoid to use general exceptions
  
* fix: add timeout to the requests
  
* fix: wrong import order
  
* fix: improve pylint disables in code
  
* docs: update the README.rst
  
* fix: improve the exception to avoiding too general exception
  
* chore: avoid being too restrictive in the constraint edx-opaque-keys
  
* chore: update requirements
  

#### Features

* add support for JWT authentication ([#258](https://github.com/eduNEXT/eox-core/issues/258)) ([292679d](https://github.com/eduNEXT/eox-core/commit/292679d9a65567a9ef221dbb641918a32695d836))

#### Performance Improvements

* add palm support DS-703 ([#254](https://github.com/eduNEXT/eox-core/issues/254)) ([732c1bf](https://github.com/eduNEXT/eox-core/commit/732c1bf6ff23a4f5c9098129217d11711e18ac88))

#### Code Refactoring

* remove all unused backends DS-703 ([#257](https://github.com/eduNEXT/eox-core/issues/257)) ([2b0c080](https://github.com/eduNEXT/eox-core/commit/2b0c0804f0ae7eae10f6898a28fb1fc05b287c2a))
* remove openedx-events constraint to use what's installed ([#252](https://github.com/eduNEXT/eox-core/issues/252)) ([8f3c550](https://github.com/eduNEXT/eox-core/commit/8f3c550726599b7c82b90ab453b1e5309152a460))

## [v8.2.0](https://github.com/eduNEXT/eox-core/compare/v8.1.0...v8.2.0) - 2023-11-18

### [8.2.0](https://github.com/eduNEXT/eox-core/compare/v8.1.0...v8.2.0) (2023-11-18)

#### Features

- add string represantion to exc_value ([#251](https://github.com/eduNEXT/eox-core/issues/251)) ([1eacfb5](https://github.com/eduNEXT/eox-core/commit/1eacfb5fd5ad43cc69ede869e8227d59c3fc818d)), closes [/github.com/eduNEXT/eox-core/blob/v6.1.0/eox_core/integrations/sentry.py#L154](https://github.com/eduNEXT//github.com/eduNEXT/eox-core/blob/v6.1.0/eox_core/integrations/sentry.py/issues/L154)

## [v8.1.0](https://github.com/eduNEXT/eox-core/compare/v8.0.0...v8.1.0) - 2023-03-20

### [8.1.0](https://github.com/eduNEXT/eox-core/compare/v8.0.0...v8.1.0) (2023-03-20)

#### Features

- allow sentry to receive extra params ([#248](https://github.com/eduNEXT/eox-core/issues/248)) ([3773f3d](https://github.com/eduNEXT/eox-core/commit/3773f3d74136f47a10ba49751744235e782324d0))

## [v8.0.0](https://github.com/eduNEXT/eox-core/compare/v7.2.3...v8.0.0) - 2023-01-31

### [8.0.0](https://github.com/eduNEXT/eox-core/compare/v7.2.3...v8.0.0) (2023-01-31)

#### ⚠ BREAKING CHANGES

- add compatibility with olive

#### Performance Improvements

- add compatibility with Open edX olive release ([#244](https://github.com/eduNEXT/eox-core/issues/244)) ([517b603](https://github.com/eduNEXT/eox-core/commit/517b603e593648d9cfbb1152349f9909b93547f9))

## [v7.2.3](https://github.com/eduNEXT/eox-core/compare/v7.2.2...v7.2.3) - 2023-01-12

### [7.2.3](https://github.com/eduNEXT/eox-core/compare/v7.2.2...v7.2.3) (2023-01-12)

### Bug Fixes

- unboundLocalError for enrollment backend ([#242](https://github.com/eduNEXT/eox-core/issues/242)) ([9bd13a7](https://github.com/eduNEXT/eox-core/commit/9bd13a7796b9c8dfebbc4dbcd14a4bd058565833))

## [v7.2.2](https://github.com/eduNEXT/eox-core/compare/v7.2.1...v7.2.2) - 2022-12-27

### [7.2.2](https://github.com/eduNEXT/eox-core/compare/v7.2.1...v7.2.2) (2022-12-27)

### Bug Fixes

- update requirements ([#239](https://github.com/eduNEXT/eox-core/issues/239)) ([a49f80a](https://github.com/eduNEXT/eox-core/commit/a49f80afc9fb39be853f2c30112b73cda6573d0d))

### Continuous Integration

- adds mantainer group ([6532c3e](https://github.com/eduNEXT/eox-core/commit/6532c3eb58848e514794e10358834d5bd9a3ef06))

## [v7.2.1](https://github.com/eduNEXT/eox-core/compare/v7.2.0...v7.2.1) - 2022-12-21

### [7.2.1](https://github.com/eduNEXT/eox-core/compare/v7.2.0...v7.2.1) (2022-12-21)

### Bug Fixes

- **ci:** update bumpversion workflow to make changelog publish ([935439c](https://github.com/eduNEXT/eox-core/commit/935439c4a513fcaaf14bb9472a0c44539459509f))

## [v7.2.0](https://github.com/eduNEXT/eox-core/compare/v7.1.0...v7.2.0) - 2022-12-16

### [7.2.0](https://github.com/eduNEXT/eox-core/compare/v7.1.0...v7.2.0) (2022-12-16)

### Features

- feat: add endpoint to create edxapp Oauth Application

## [v7.1.0](https://github.com/eduNEXT/eox-core/compare/v7.0.1...v7.1.0) - 2022-12-16

### [7.1.0](https://github.com/eduNEXT/eox-core/compare/v7.0.1...v7.1.0) (2022-12-16)

### Features

- feat: Make extra registration fields optional in during edxapp account creation

## [v7.0.1](https://github.com/eduNEXT/eox-core/compare/v7.0.0...v7.0.1) - 2022-12-13

### [7.0.1](https://github.com/eduNEXT/eox-core/compare/v7.0.0...v7.0.1) (2022-12-13)

### Fixes

- fix: update md4 to md5

## [v7.0.0](https://github.com/eduNEXT/eox-core/compare/v6.1.2...v7.0.0) - 2022-10-07

### [7.0.0](https://github.com/eduNEXT/eox-core/compare/v6.1.2...v7.0.0) (2022-10-07)

#### ⚠ BREAKING CHANGES

- drop django22 and added python 3.10
- feat: make it compatible with nutmeg
- perf: update requirements
- docs: update readme
- feat: drop django22 and added python 3.10
- ci: add python publish workflow and drop circleci

Co-authored-by: Maria Fernanda Magallanes Zubillaga [maria.magallanes@edunext.co](mailto:maria.magallanes@edunext.co)
Co-authored-by: Juan David Buitrago [juan.buitrago@edunext.co](mailto:juan.buitrago@edunext.co)

#### Performance Improvements

- plugin compatible with nutmeg  ([#216](https://github.com/eduNEXT/eox-core/issues/216)) ([22f60b5](https://github.com/eduNEXT/eox-core/commit/22f60b5b2f4266918c976c9505692ba0a99e57db))

#### Documentation

- update CHANGELOG ([1e20266](https://github.com/eduNEXT/eox-core/commit/1e202662afcb9eca7893f9c36d3a9de3dba831ea))

## [v6.1.2](https://github.com/eduNEXT/eox-core/compare/v6.1.1...v6.1.2) - 2022-10-04

### [6.1.2](https://github.com/eduNEXT/eox-core/compare/v6.1.1...v6.1.2) (2022-10-04)

### Bug Fixes

- remove try except and correct platform path ([8a23616](https://github.com/eduNEXT/eox-core/commit/8a236161e09e81d1d330cf77e6dc6265a4e64256))

### Continuous Integration

- update workflows commitlint and rm commitlint.config file ([39c011c](https://github.com/eduNEXT/eox-core/commit/39c011c164f9d07960a5550426e770d8b268389c))

### Documentation

- update CHANGELOG ([#209](https://github.com/eduNEXT/eox-core/issues/209)) ([592daf3](https://github.com/eduNEXT/eox-core/commit/592daf3e95f624d0359cfae4d88ebd18567e0243))

## [v6.1.1](https://github.com/eduNEXT/eox-core/compare/v6.1.0...v6.1.1) - 2022-06-03

### [6.1.1](https://github.com/eduNEXT/eox-core/compare/v6.1.0...v6.1.1) (2022-06-03)

### Bug Fixes

- get settings course_org_filter when validating org for async proc ([d4987ca](https://github.com/eduNEXT/eox-core/commit/d4987ca7c2e1df2242cfb2c4cf8b2261dec27a2f))

## [v6.1.0](https://github.com/eduNEXT/eox-core/compare/v6.0.2...v6.1.0) - 2022-05-25

## [6.1.0](https://github.com/eduNEXT/eox-core/compare/v6.0.2...v6.1.0) (2022-05-25)

### Features

- add more useful functions to certificates backend ([#206](https://github.com/eduNEXT/eox-core/issues/206)) ([e3109d2](https://github.com/eduNEXT/eox-core/commit/e3109d29c7fb68b01931859dd84a70a83c4b4cf6))

### Documentation

- update CHANGELOG ([#203](https://github.com/eduNEXT/eox-core/issues/203)) ([c2d8d37](https://github.com/eduNEXT/eox-core/commit/c2d8d37707fb0b7b83b9efa493abf3e1cc068edc))
- update issue templates ([bdb93ad](https://github.com/eduNEXT/eox-core/commit/bdb93adb10c11a2ac6bf8f6ae5ca685619bb4a42))

## [v6.0.2](https://github.com/eduNEXT/eox-core/compare/v6.0.1...v6.0.2) - 2022-04-13

### [6.0.2](https://github.com/eduNEXT/eox-core/compare/v6.0.1...v6.0.2) (2022-04-13)

### Bug Fixes

- solve issue with api_doc_tools and update requirements ([#202](https://github.com/eduNEXT/eox-core/issues/202)) ([27d7eac](https://github.com/eduNEXT/eox-core/commit/27d7eac0963449864f2d98d696559b79abd88214))

### Documentation

- update CHANGELOG ([#201](https://github.com/eduNEXT/eox-core/issues/201)) ([1936190](https://github.com/eduNEXT/eox-core/commit/19361903b16d9e38172dbce1ea9ac472f8462a0c))

## [v6.0.1](https://github.com/eduNEXT/eox-core/compare/v6.0.0...v6.0.1) - 2022-03-07

### [6.0.1](https://github.com/eduNEXT/eox-core/compare/v6.0.0...v6.0.1) (2022-03-07)

### Bug Fixes

- replace create commit with create pr ([#200](https://github.com/eduNEXT/eox-core/issues/200)) ([b5e7336](https://github.com/eduNEXT/eox-core/commit/b5e733677c4cc0ee53038c2cd7b68d3f2a118c9b))
- **ci:** solve issue with bumpversion on github ([320a698](https://github.com/eduNEXT/eox-core/commit/320a698b875071fa02884455573cb576e1c9a1d4))

### Documentation

- update CHANGELOG ([#199](https://github.com/eduNEXT/eox-core/issues/199)) ([c96ab12](https://github.com/eduNEXT/eox-core/commit/c96ab12940bd46d4489508274830658ece92114f))

### Continuous Integration

- add python tests action to github workflows ([#196](https://github.com/eduNEXT/eox-core/issues/196)) ([a418ab7](https://github.com/eduNEXT/eox-core/commit/a418ab7c8b0e28f16b83bb438ea88b43de2be335))

### Tests

- solve lint warnings after updating the requirements ([#198](https://github.com/eduNEXT/eox-core/issues/198)) ([0a80168](https://github.com/eduNEXT/eox-core/commit/0a8016840d550c108eda48b3050777d156c4cc96))

## [v6.0.0](https://github.com/eduNEXT/eox-core/compare/v5.1.1...v6.0.0) - 2022-03-04

## [6.0.0](https://github.com/eduNEXT/eox-core/compare/v5.1.1...v6.0.0) (2022-03-04)

### ⚠ BREAKING CHANGES

- remove the Course Management feature
- **django32:** Drop python 3.5 support in favor of python 3.8.

### Performance Improvements

- **django32:** add compatibility with openedx maple release ([#197](https://github.com/eduNEXT/eox-core/issues/197)) ([74a6160](https://github.com/eduNEXT/eox-core/commit/74a61607080dc33be6d3f57dcac254b640b37076))

### Documentation

- change extension of CHANGELOG file to markdown ([effcef8](https://github.com/eduNEXT/eox-core/commit/effcef8beb0fa48901044fbcdfeaf59b2b9c62e4))

### Continuous Integration

- add bumpversion action to github workflows ([#192](https://github.com/eduNEXT/eox-core/issues/192)) ([99a4516](https://github.com/eduNEXT/eox-core/commit/99a4516eef22e16441a5665758a5ceb2c93045fd))
- add changelog update job to bump_version workflow ([6f758de](https://github.com/eduNEXT/eox-core/commit/6f758deada55c428763474f8997c1d23e85e5d46))
- add commitlint action to github workflows ([#194](https://github.com/eduNEXT/eox-core/issues/194)) ([88da568](https://github.com/eduNEXT/eox-core/commit/88da56886002582a3a80570273c3ff18c6b10c73))
- add conditional to run changelog update action ([#195](https://github.com/eduNEXT/eox-core/issues/195)) ([1595948](https://github.com/eduNEXT/eox-core/commit/1595948044e895bd26df18605289d06e53e940b0))

### Code Refactoring

- remove the Course Management feature ([c0c3b55](https://github.com/eduNEXT/eox-core/commit/c0c3b558382c39d4986b2a5e178ce3f1aef47f8a))

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
