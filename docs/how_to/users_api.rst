Extra Profile Fields
==========

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
