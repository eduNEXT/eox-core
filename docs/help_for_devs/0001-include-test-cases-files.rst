###################
Eox-core test cases
###################

Status
------

Accepted

Context
-------

In order to have a way to test the eox-core API endpoints manually, but quickly, two json files have been
created with the GET, POST, PATCH and DELETE requests. The `Eox-core-test.postman_collection.json`_ and
`Eox-core-test.postman_environment.json`_ files were created with the `Posman`_ application.

.. _Eox-core-test.postman_collection.json: ../resources/Eox-core-test.postman_collection.json
.. _Eox-core-test.postman_environment.json: ../resources/Eox-core-test.postman_environment.json
.. _Posman: https://www.postman.com/

Instructions
------------

To test the endpoints it is necessary to have the Open Edx platform running with the eox-core plugin installed.

#. Once your environment is set up, create a new admin user: ``tutor dev createuser -staf - superuser admin <custom-mail> -p <password>``.
#. Log into Django's admin site using the user created in the previous step.
#. On the Site Administration panel go to *Authentication and Authorization* > *Users*.
#. Click on the admin user created on the first step.
#. Go to User permissions and look for auth **user** *can access eox-core API* and add it with a double click or one click and right arrow.
#. Click Save at the bottom of the page.
#. On the Site Administration panel go to *Django Oauth Toolkit* > *Applications*.
#. You should be redirected to a table with a bunch of applications and on the right upper corner there's a button to Add *Application*, click on it.
#. Once again, you should be redirected to a new page with a bunch of blank spaces, nevertheless, *client id* and *client secret* are given. Save them, as you will need these later.
#. Fill the left spaces with the following rules:

    - For *User id* click on the magnifier icon next to the blank space, a window should show up with the app's users, pick the one you created in the first step.
    - On the *Redirect to URL* section add your app's url.
    - Pick *Confidential* on the *Client type* dropdown menu.
    - Pick *Client credentials* for *Authorization grant type*.
    - Add a custom *name*.

#. Once everything is filled, click Save.
#. In this test the desktop Postman application was used. Postman for Linux Version 8.12.5.
#. Download the json files with the test (collection and environment).
#. On *import* > *upload files*, upload the json files. Once it's uploaded, it should be shown in *Collections* and *Environments* menu.
#. For *Collections*, there should be an arrow on the left side of the name, click on it to extend the content. The file consists of 3 folders:

    - Main API
        * User
            + Create user
            + Get user
            + Update user
        * Enrollment
            + Create enrollment
            + Get enrollment
            + Update enrollment
            + Delete enrollment
            + Create enrollment to test grade
        * Pre enrollment
            + Create whitelistings
            + Get regular pre-enrollment
            + Update whitelistings
            + Delete pre-enrollment
        * Grade
            + Grade information
        * User info
            + Get user related to the authorization token
    - Task dispatcher API
            + Get task
            + Dispatch a task
            + Check the status
    - Support API
            + Update username
            + Delete User

    plus an Authorization section. Click on the last one.

#. More in depth information about the Authorization section should be now displayed on the right side panel. It looks more familiar to a traditional postman request. Go to the body and a table with 3 keys with their values should be displayed. Change this values in Environment.
#. For *Environment* a table on the right panel should appear with the following headers: *variable*, *initial value*, *current value*. Change the *client_id* and *client_secret* with those values retrieved from the *Django Oauth Toolkit*.

    .. image:: ../resources/variables_env.png
        :height: 300
        :width: 900
        :alt: Environment variable

#. Edit all variables except token and task_id, these are auto-generated
#. Once again, pick the uploaded files in the Collections panel.
#. On the right top side of the app, make sure your environment with the variables is chosen, if so click on the three dots shown when hovering the file's name and click on run collection. This should run all the tests at once and the result will be shown on the right panel.
