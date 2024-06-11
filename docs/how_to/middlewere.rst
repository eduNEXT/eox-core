Middleware
==========

Eox-core implements the next middleware:

Redirection Middleware
----------------------

Allow redirection to other domains or error pages. Set in the LMS configuration: 

.. code-block::
   
   USE_REDIRECTION_MIDDLEWARE = True

Open the Django Admin and check the *eduNEXT Openedx Extensions › Redirections* model to configure the redirection. 

Path Redirection Middleware
---------------------------

Create custom responses based on the request path. Use the settings in the LMS:

- ``EDNX_CUSTOM_PATH_REDIRECTS``: Redirect based on an action.
   
+---------------------+-----------------------------------------------------------------------+
| Action              | Description                                                           |
+=====================+=======================================================================+
| login_required      | Redirect to the login page if the user doesn't have an active session.|
+---------------------+-----------------------------------------------------------------------+
| not_found           | Return 404.                                                           |
+---------------------+-----------------------------------------------------------------------+
| not_found_loggedin  | Return 404 for authenticated users.                                   |
+---------------------+-----------------------------------------------------------------------+
| not_found_loggedout | Return 404 for unauthenticated users.                                 |
+---------------------+-----------------------------------------------------------------------+
| redirect_always     | Send to the given target.                                             |
+---------------------+-----------------------------------------------------------------------+
| redirect_loggedin   | Redirect authenticated users to the target.                           |
+---------------------+-----------------------------------------------------------------------+
| redirect_loggedout  | Redirect unauthenticated users to the given target.                   |
+---------------------+-----------------------------------------------------------------------+

An example of how to implement it:

.. code-block::
    
      EDNX_CUSTOM_PATH_REDIRECTS = {
        "/$": {
            "not_found": ""
        },
        "/courses/{COURSE_ID_PATTERN}/about": {                     # Path
            "redirect_always": "https://redirection.example.com"    # Action: Target
        },
        "/register.*": {
            "redirect_loggedin": "https://redirection.example.com"
        }
    }


- ``MKTG_REDIRECTS``: Redirect for specific pages. 

.. code-block::

       "MKTG_REDIRECTS": {
          "about.html": "",                                     # Use the normal LMS page
          "contact.html": "https://redirection.example.com",    # Redict to the given target
          "faq.html": "",
          "honor.html": "",
          "privacy.html": "",
          "tos.html": ""
        }
   
TPA Exception Middleware
------------------------

Handle exceptions not caught by Social Django.


User Language Preference Middleware
-----------------------------------

Allow the user to set the language preference for the site. 
