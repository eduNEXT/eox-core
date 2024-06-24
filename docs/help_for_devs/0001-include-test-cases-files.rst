###################
Eox-core test cases
###################

Context
-------

To have a way to test the eox-core API endpoints manually, but quickly, two JSON files have been
created with GET, POST, PATCH, and DELETE requests. The `Eox-core Test Collection`_ and
`Eox-core Test Environment`_ files were created for the `Postman`_ application.

.. _Eox-core Test Collection: ../resources/eox-core-test.postman_collection.json
.. _Eox-core Test Environment: ../resources/eox-core-test.postman_environment.json
.. _Postman: https://www.postman.com/

Instructions
------------

To properly test the endpoints, the Open Edx platform must be running with the eox-core plugin installed.

#. Once your environment is set up, create a new admin user: ``tutor dev do createuser --staff --superuser admin <custom-mail> --password <password>``.
#. Log into Django's admin site with the user created in the previous step.
#. Create a testing user without staff permissions, you could do this on the Django admin page.

   🚨 Some of the tests will require a staff user, specifically those for the support API; if you want to run the test collection at once, use the 
   admin user and skip the permission assignment steps.

#. On the Site Administration Panel, go to *Authentication and Authorization* > *Users*.
#. Click on the testing user created by the third step.
#. Go to User Permissions, search for ``auth | user | Can access eox-core API`` and add it with a double click or one click and the right arrow.
#. Click Save at the bottom of the page.
#. On the Site Administration panel, go to *Django Oauth Toolkit* > *Applications*.
#. Once there, in the right-upper corner, you will find the *Add Application* button, click on it.
#. You should be redirected to a new page with a bunch of blank spaces, nevertheless, *client id* and *client secret* are given. Save them, as you will need them later.
#. Fill the blank spaces with the following rules:

   - For *User id* click on the magnifying glass icon, and a window should appear with the app's users. Select the one you created for testing.
   - On the *Redirect to URL* section add your app URL.
   - Pick *Confidential* on the *Client type* dropdown menu.
   - Pick *Client credentials* for *Authorization grant type*.
   - Add a custom *name*.

#. Once everything is filled, click Save.
#. Open the desktop Postman application. and load the test collection and environment provided. On *import* > *upload files*, add the JSON files. 
   Once it's uploaded, it should be shown in the *Collections* and *Environments* menu.
#. For *Collections*, there should be an arrow on the left side of the name, click on it to extend the content. The file structure:

   .. code-block::
        
        Eox-core
        |
        ├── Main API
        │   ├── User
        │   │   ├── Create user
        │   │   ├── Get user
        │   │   └── Update user
        │   ├── Enrollment
        │   │   ├── Create enrollment
        │   │   ├── Get enrollment
        │   │   ├── Update enrollment
        │   │   ├── Delete enrollment
        │   │   └── Create enrollment to test grade
        │   ├── Pre-enrollment
        │   │   ├── Create whitelisting
        │   │   ├── Get regular pre-enrollment
        │   │   ├── Update whitelisting
        │   │   └── Delete pre-enrollment
        │   ├── Grade
        │   │   └── Grade information
        │   └── User info
        │       └── Get user related to the authorization token
        ├── Task dispatcher API
        │   ├── Get task
        │   ├── Dispatch a task
        │   └── Check the status
        ├── Support API
        │   ├── Update username
        │   └── Delete User
        └── Authentication

#. Open the Authentication POST request and go to the body, a table with 3 keys and values should be displayed. Those values must be updated with the eox-core Environment.
#. For *Environment* a table on the right panel should appear with the following headers: *variable*, *initial value* and *current value*. Modify the *client_id* and
   *client_secret* with those values retrieved from the *Django Oauth Toolkit*.

   .. image:: ../resources/variables_env.png
        :height: 300
        :width: 900
        :alt: Environment variable

#. Edit all variables except token and task_id, these are auto-generated
#. Go back to the to Collection panel.
#. On the right-top side of the app, make sure eox-core environment is chosen and updated, if so click on the three dots shown when hovering over the file's name and click on *Run collection*. This should carry out all the tests at once and the result will be displayed.
