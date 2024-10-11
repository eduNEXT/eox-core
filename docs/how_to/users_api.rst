Users API Documentation
=======================

**Get User**

URL: ``/eox-core/api/v1/user/``

Method: GET

Query Params:

    username (String)

    email (String)

Example:

   http://tenant-a.local.edly.io:8000/eox-core/api/v1/user/?username=johndoe

   http://tenant-a.local.edly.io:8000/eox-core/api/v1/user/?email=johndoe@example.com

    
Response Example:

.. code-block:: json

   200 OK

   {
      "account_privacy": "private",
      "profile_image": {
         "has_image": false,
         "image_url_full": "http://tenant-a.local.edly.io:8000/static/images/profiles/default_500.png",
         "image_url_large": "http://tenant-a.local.edly.io:8000/static/images/profiles/default_120.png",
         "image_url_medium": "http://tenant-a.local.edly.io:8000/static/images/profiles/default_50.png",
         "image_url_small": "http://tenant-a.local.edly.io:8000/static/images/profiles/default_30.png"
      },
      "username": "johndoe",
      "bio": null,
      "course_certificates": null,
      "country": null,
      "date_joined": "2024-07-18T17:19:10Z",
      "language_proficiencies": [],
      "level_of_education": null,
      "social_links": [],
      "time_zone": null,
      "name": "John Doe",
      "email": "johndoe@example.com",
      "id": 6,
      "verified_name": null,
      "extended_profile": [],
      "gender": null,
      "state": null,
      "goals": "",
      "is_active": false,
      "last_login": null,
      "mailing_address": "",
      "requires_parental_consent": true,
      "secondary_email": null,
      "secondary_email_enabled": null,
      "year_of_birth": null,
      "phone_number": null,
      "activation_key": "0511129811d04152bdb3ae49fa64c0eb",
      "pending_name_change": null
   }


**Create User**

URL: ``/eox-core/api/v1/user/``

Method: POST

Body:

.. code-block:: json

   {
      "username": "johndoe",
      "email": "johndoe@example.com",
      "fullname": "John Doe",
      "password": "p@ssword"
   }

Response Example:

.. code-block:: json

   200 OK

   {
      "email": "johndoe@example.com",
      "username": "johndoe",
      "is_active": false,
      "is_staff": false,
      "is_superuser": false
   }



**Extra Profile Fields**

**Creating custom registration fields**

**Tenant settings**

Add the following settings to the microsite where we want to add the fields:

Example: Adding a custom field

If, for example, we want to add the field `Organization name`, we will have to do the following:

1. Add the field name, `org_name` for example, to `extended_profile_fields`. This indicates that `org_name` will be saved as an extended profile field.

.. code-block:: json

    "extended_profile_fields": [ "org_name" ]

2. Add org_name to REGISTRATION_EXTRA_FIELDS, indicating whether the field is hidden, optional, or required:

.. code-block:: json

  "REGISTRATION_EXTRA_FIELDS": {
      "org_name": "required"
  }

3. In this step, we will create the custom field as a dictionary. In this case, we are going to create a text field for org_name. We must indicate: name, type, and label as the minimum:

.. code-block:: json

  "EDNX_CUSTOM_REGISTRATION_FIELDS": [
      {
          "name": "org_name",
          "type": "text",
          "label": "Organization name"
      }
  ]


**Update User**

URL: ``/eox-core/api/v1/update-user/``

Method: PATCH

Body:

.. code-block:: json

   {
      "email": "johndoe-updated@example.com",
      "password": "updated-p@$$w0rd"
   }

Example:

   http://tenant-a.local.edly.io:8000/eox-core/api/v1/update-user/

Response Example:

.. code-block:: json

   200 OK

