Integration tests
=================

.. contents::

Enrollments API
+++++++++++++++

Running
-------

You can run the tests using the make target

.. code-block:: console

    $ make python-test

This test make several assumptions about the current state of the database
in case your setup differs you will have to modify ``test_data`` accordingly.

Data requirements
-----------------
The test_data file includes the data necessary to run each test. It's content
must reflect the current database configuration of the platform you
are running the tests. The provided test are meant to be run on a devstack
environment with the following requirements:

1. There should be a DOT application with client_id ``apiclient`` and
   client_secret ``apisecret``
2. There should be two sites available with Domain Name ``site1.localhost`` and
   ``site2.localhost``
3. Each site should have one user with username ``user_site1`` and email
   ``user_site1@example.com`` for ``site1`` and ``user_site2`` and
   ``user_site2@example.com`` for ``site2``.
4. ``site1`` should have a ``site1_course`` with id
   ``course-v1:edX+DemoX+Demo_Course`` this course should not be available on
   ``site2``. You must enable the ``audit`` and ``honor`` modes for ``site1_course``

``test_data`` layout
~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "site1_data": {
            "fake_user": "fakeuser",
            "user_id": "user_site1",
            "user_email": "user_site1@example.com",
            "host": "site1.localhost",
            "course": {
                "id": "course-v1:edX+DemoX+Demo_Course",
                "mode": "audit"
            },
            "base_url": "http://site1.localhost:18000",
            "client_id": "apiclient",
            "client_secret": "apisecret"
        },
        "site2_data": {
            "user_id": "user_site2",
            "user_email": "user_site2@example.com",
            "host": "site2.localhost",
            "base_url": "http://site2.localhost:18000",
            "client_id": "apiclient",
            "client_secret": "apisecret"
        }
    }

Current Tests
-------------

Each test from this suite performs an http request to guarantee
that all CRUD operations are handled correctly. Each test case
is detailed below, including arguments used in each request
with data from ``test_data``.

Create
~~~~~~

  .. code::

    SetUp   1-7: Delete previous enrollments

  1. Create a valid enrollment  ✔
  2. Create a valid enrollment using force ✔
  3. Create an enrollment with invalid user ❌
  4. Create an enrollment with user from another site ❌
  5. Create an enrollment with invalid course ❌
  6. Create an enrollment with course from another site ❌
  7. Create an enrollment with invalid mode ❌


**Requests arguments**

.. list-table::


  * - Nº
    - Method
    - User
    - Course
    - Mode
    - Site
    - Force

  * - 1
    - POST
    - ``user_site1``
    - ``site1_course``
    - ``audit``
    - ``site1``
    - ``False``

  * - 2
    - POST
    - ``user_site1``
    - ``site1_course``
    - ``audit``
    - ``site1``
    - ``True``

  * - 3
    - POST
    - ``site1_fakeuser``
    - ``site1_course``
    - ``audit``
    - ``site1``
    - ``False``

  * - 4
    - POST
    - ``user_site2``
    - ``site1_course``
    - ``audit``
    - ``site1``
    - ``False``

  * - 5
    - POST
    - ``user_site1``
    - ``site1_fakecourse``
    - ``audit``
    - ``site1``
    - ``True``

  * - 6
    - POST
    - ``user_site2``
    - ``site1_course``
    - ``audit``
    - ``site2``
    - ``True``

  * - 7
    - POST
    - ``user_site1``
    - ``site1_course``
    - ``Masters``
    - ``site1``
    - ``True``

READ
~~~~

  .. code::

    SetUp   1,3: Create default enrollment
    SetUp     2: Delete previous enrollments

  1. Read a valid enrollment  ✔
  2. Read a non-existent enrollment ❌
  3. Read an existing enrollment from another site ❌

**Requests arguments**

.. list-table::

  * - Nº
    - Method
    - User
    - Course
    - Site

  * - 1
    - GET
    - ``user_site1``
    - ``site1_course``
    - ``site1``

  * - 2
    - GET
    - ``user_site1``
    - ``site1_course``
    - ``site1``

  * - 3
    - GET
    - ``user_site2``
    - ``site1_course``
    - ``site2``

UPDATE
~~~~~~

  .. code::

    SetUp   1-3, 6-7: Create default enrollment
    SetUp        4-5: Delete previous enrollments

  1. Change ``is_active`` ✔
  2. Change mode ✔
  3. Change to invalid mode ❌
  4. Change ``is_active`` from invalid enrollment ❌
  5. Change mode from invalid enrollment ❌
  6. Change ``is_active`` with POST force ✔
  7. Change mode with POST force ✔

**Requests arguments**

.. list-table::

  * - Nº
    - Method
    - User
    - Course
    - Mode
    - Site
    - ``is_active``

  * - 1
    - PUT
    - ``user_site1``
    - ``site1_course``
    - ``audit``
    - ``site1``
    - ``False``

  * - 2
    - PUT
    - ``user_site1``
    - ``site1_course``
    - ``honor``
    - ``site1``
    - ``True``

  * - 3
    - PUT
    - ``user_site1``
    - ``site1_course``
    - ``masters``
    - ``site1``
    - ``True``

  * - 4
    - PUT
    - ``user_site1``
    - ``site1_course``
    - ``honor``
    - ``site1``
    - ``True``

  * - 5
    - PUT
    - ``user_site1``
    - ``site1_course``
    - ``audit``
    - ``site1``
    - ``False``

.. list-table::

  * - Nº
    - Method
    - User
    - Course
    - Mode
    - Site
    - ``is_active``
    - Force

  * - 6
    - POST
    - ``user_site1``
    - ``site1_course``
    - ``audit``
    - ``site2``
    - ``False``
    - ``True``

  * - 7
    - POST
    - ``user_site1``
    - ``site1_course``
    - ``masters``
    - ``site1``
    - ``True``
    - ``True``

DELETE
~~~~~~

  .. code::

    SetUp   1,3: Create default enrollment
    SetUp     2: Delete previous enrollments

  1. Delete a valid enrollment  ✔
  2. Delete a non-existent enrollment ❌
  3. Delete an existing enrollment from another site ❌

**Requests arguments**

.. list-table::

  * - Nº
    - Method
    - User
    - Course
    - Site

  * - 1
    - DELETE
    - ``user_site1``
    - ``site1_course``
    - ``site1``

  * - 2
    - DELETE
    - ``user_site1``
    - ``site1_course``
    - ``site1``

  * - 3
    - DELETE
    - ``user_site2``
    - ``site1_course``
    - ``site2``

Testing on stage
----------------
In case you want to run the test suite on a staging server, first you must
alter the ``test_data`` file.
The prerequisites mentioned on `Data requirements`_ still apply;

1. You must have access to 2 different sites. Change:
   ``site1_data['base_url']``, ``site1_data['host']``,
   ``site2_data['base_url']``, ``site2_data['host']``
   depending on their domain name.
2. You must have an client_id and client_secret for each site. Change:
   ``site1_data['client_id']``, ``site1_data['client_secret']``,
   ``site2_data['client_id']``, ``site2_data['client_secret']``
3. You must have one user for each site. Change:
   ``site1_data['user_id']``, ``site1_data['user_email']``,
   ``site2_data['user_id']``, ``site2_data['user_email']``
4. You must have a course on site 1 that is **not** available on site 2
   with audit and honor as available modes.  Change:
   ``site1_data['course']['id']``

Grades API
+++++++++++++++

The info about Running, Data requirements and ``test_data`` layout is the same
as in `Enrollments Api`_.

Current Tests
-------------

The Grades API only supports the read operation in consequence those are the
only tests present.

READ
~~~~

  .. code::

    SetUp   : Create default enrollment

  1. Read a user's final grade in a course  ✔
  2. Read a user's final grade and by subsection in a course  ✔
  3. Read a user's final grade, by subsection and course grading policy  ✔
  4. Read a user's grade, with user and course belonging to another site. ❌

**Requests arguments**

.. list-table::

  * - Nº
    - Method
    - User
    - Course
    - Site
    - ``detailed``
    - ``grading_policy``

  * - 1
    - GET
    - ``user_site1``
    - ``site1_course``
    - ``site1``
    - ``false``
    - ``false``

  * - 2
    - GET
    - ``user_site1``
    - ``site1_course``
    - ``site1``
    - ``true``
    - ``false``

  * - 3
    - GET
    - ``user_site1``
    - ``site1_course``
    - ``site1``
    - ``true``
    - ``true``

  * - 3
    - GET
    - ``user_site1``
    - ``site1_course``
    - ``site2``
    - ``true``
    - ``true``

Testing on stage
----------------

Follow steps 1-3 from the `Enrollments API`_  *Testing on stage* instructions.
