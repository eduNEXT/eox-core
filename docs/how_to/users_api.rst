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

The User API supports the use of extra and custom registration fields for both Create and Update operations. This allows for flexibility in managing user profiles with additional fields beyond the default ones, ensuring that tenants can extend user data as needed.

**Creating custom registration fields**

**Tenant settings**

To add custom or extra registration fields for a specific tenant, you'll need to configure the following settings:

Example: Adding a custom field
------------------------------

If, for example, we want to add the field `Organization name`, we will have to do the following:

1. Add the field name, `org_name` for example, to `extended_profile_fields` setting. This indicates that `org_name` will be saved as an extended profile field.

   .. code-block:: json

      "extended_profile_fields": [ "org_name" ]

2. Add `org_name` to `REGISTRATION_EXTRA_FIELDS` setting, indicating whether the field is hidden, optional, or required:

   .. code-block:: json

      "REGISTRATION_EXTRA_FIELDS": {
         "org_name": "required"
      }

### Note on Hidden Fields

Fields that are set as `hidden` in the configuration will not be visible in the registration form or user profile, and they **cannot be updated through the API**.

If you attempt to update a field that is marked as `hidden` using the API, the update will be ignored, and no changes will be applied to that field.

3. Define the custom field by creating it as a dictionary inside the `EDNX_CUSTOM_REGISTRATION_FIELDS` setting. In this case, we are creating a text field for `org_name`. You must specify at least the `name`, `type`, and `label`:

   .. code-block:: json

      "EDNX_CUSTOM_REGISTRATION_FIELDS": [
         {
            "name": "org_name",
            "type": "text",
            "label": "Organization name"
         }
      ]

Once the field is configured, it can be included in the body of both `POST` (to create a new user) and `PATCH` (to update an existing user) requests.

**Types of Custom Fields**
--------------------------

You can create various types of fields to customize the registration form, depending on the type of input you want to collect. Here are some examples:

**Text Field**

A simple text input field, used for collecting short text responses like a PIN or Student ID:

.. code-block:: json

   {
      "name": "pin_id",
      "type": "text",
      "label": "PIN / Student ID:"
   }

**Checkbox**

A checkbox field, often used for consent or binary choices:

.. code-block:: json

   {
      "name": "data_consent",
      "type": "checkbox",
      "label": "I wish to receive information about courses, events, etc."
   }

**Select (Dropdown)**

A dropdown field that allows users to choose from a predefined list of options. You can also set a default value:

.. code-block:: json

   {
      "name": "company_dependence",
      "type": "select",
      "label": "Establishment dependency.",
      "options": ["Municipal", "Subsidized private", "Paid private"],
      "default": "Municipal"
   }

**Field Visibility Options**
----------------------------

When configuring additional registration fields, there are several visibility and requirement options that can be used:

- **required**: The field is displayed and must be filled out by the user.
- **`optional`**: The field is displayed as part of a toggled input field list, and it is not mandatory to fill it out.
- **`hidden`**: The field is not displayed to the user.
- **`optional-exposed`**: The field is displayed along with the required fields, but filling it out is not mandatory. This option provides more visibility than `optional` while still keeping the field optional.

**Testing `optional-exposed`**

If you want to use and test the `optional-exposed` field type, make sure to add it to the configuration. For example, you can set a field to `optional-exposed` like this:

.. code-block:: json

   "REGISTRATION_EXTRA_FIELDS": {
      "org_name": "optional-exposed"
   }

In this case, the `org_name` field will be displayed alongside required fields, but it won't be mandatory for the user to fill out. This can be particularly useful for fields that are not crucial but should be easily visible to users during registration.

**Example Usage**

Here is an example configuration using all the types, including `optional-exposed`:

.. code-block:: json

   "REGISTRATION_EXTRA_FIELDS": {
      "confirm_email": "hidden",
      "level_of_education": "optional",
      "gender": "optional-exposed",
      "year_of_birth": "optional",
      "mailing_address": "optional-exposed",
      "honor_code": "required"
   }

In this example:

- `gender` and `mailing_address` are set to `optional-exposed`, making them visible alongside required fields but not mandatory.
- `honor_code` is `required`, ensuring it must be filled.
- `level_of_education` and `year_of_birth` are optional and shown in a secondary list.
- `confirm_email` is hidden from the registration form.

**Including the custom field in a POST request:**

.. code-block:: json

   {
      "username": "johndoe",
      "email": "johndoe@example.com",
      "fullname": "John Doe",
      "password": "p@ssword",
      "org_name": "Tech Solutions"
   }

**Including the custom field in a PATCH request:**

.. code-block:: json

   {
      "email": "johndoe-updated@example.com",
      "org_name": "New Organization Name"
   }

By following these steps, the `org_name` field will be correctly handled during user creation or update.



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

**EOX_CORE_USER_UPDATE_SAFE_FIELDS**
------------------------------------

This setting changes that allow specific user profile fields, considered as 'safe', to be updated. These "safe" fields are defined in the setting `EOX_CORE_USER_UPDATE_SAFE_FIELDS`.

### Safe Fields Update

The `EOX_CORE_USER_UPDATE_SAFE_FIELDS` setting specifies which fields in the user profile can be updated without requiring additional permissions.

Example configuration of `EOX_CORE_USER_UPDATE_SAFE_FIELDS`:

.. code-block:: json

   "EOX_CORE_USER_UPDATE_SAFE_FIELDS": [
      "bio",
      "profile_image",
      "language",
   ]

### Update User Endpoint Enhancement

A modification was also made to the update user endpoint, allowing it to filter users by `username` or `email`. This makes it easier to identify and update a specific user directly using one of these parameters.

To use the filtering capabilities, the endpoint can be accessed as follows:

**URL**: ``/eox-core/api/v1/update-user/``

**Method**: PATCH

**Query Parameters**:

- `username`: Specify the username of the user to update.
- `email`: Specify the email of the user to update.

**Example Usage**:

.. code-block:: http

   PATCH http://tenant-a.local.edly.io:8000/eox-core/api/v1/update-user/?username=johndoe

   PATCH http://tenant-a.local.edly.io:8000/eox-core/api/v1/update-user/?email=johndoe@example.com

**Example Body**:

.. code-block:: json

   {
      "bio": "Updated user bio.",
      "language": ["en", "es"]
   }

**Response Example**:

.. code-block:: json

   200 OK

   {
      "username": "johndoe",
      "bio": "Updated user bio.",
      "language": ["en", "es"]
   }