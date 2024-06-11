Application Programming Interface
=================================

The API is usable only if the user is authenticated or has the right permissions.

For authentication, an authorization token could be sent in the headers of the request, otherwise the session authentication will be used.

For permissions, the user should be configured with ``auth | user | Can access eox-core API`` or be set as an admin. 

Endpoints
---------

A Swagger application has been configured for the easy use of the eox-core API, you can access it with ``/eox-core/api-docs/#/`` path, you will find the available endpoints and examples for each one.

**Enrollment** ``/eox-core/api/v1/enrollment/``

- GET: Retrieves enrollment information given a user and a course_id.
- POST: Enroll a user(s) in a course.
- PUT: Update enrollment for the given user.
- DELETE: Remove enrollment for a user.


**Grade** ``/eox-core/api/v1/grade/``

- GET: Retrieves Grades information for given a user and course_id.

**User** ``/eox-core/api/v1/user/``

- GET: Retrieve a user given the email or username as a query param.
- POST: Create a new user.
- PATCH: Update user information. Use the endpoint ``/eox-core/api/v1/update-user/``.

Some additional endpoints are less frequently used or have to be managed carefully, these are not available in Swagger but you can find them in the Postman collection created for testing:

**Pre-enrollment** ``/eox-core/api/v1/pre-enrollment/``

- POST: Create a new register of the given user in the whitelist of the course.
- PUT: Given a course_id and the user email update their pre-enrollment status.
- DELETE: Remove the pre-enrollment of a user in a course.
- GET: Retrieve the pre-enrollment status of a user if this has one in the given course. 

**Celery task dispatcher** ``/eox-core/tasks-api/v1/tasks/``

- GET: Check the status of a celery task given an id as a query param.
- POST: Dispatch a task to a celery worker. The task must be registered in the worker and has to be enabled in the setting ``EOX_CORE_ASYNC_TASKS``.

**Support**

- PATCH: Allow to safely update the username along with the forum-associated user. Users with different sig up cannot be updated.
- DELETE: Remove a user safely. 
