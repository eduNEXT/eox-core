Pipeline
========

Define functions that are used in the third-party authentication flow.

+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| Pipeline                                 | Description                                                                                                                              |
+==========================================+==========================================================================================================================================+
| ensure_new_user_has_usable_password      | Assign a usable password to a user in case it has an unusable password on user creation.                                                 |
|                                          | At the creation of new users through some TPA providers, some of them are created with an unusable password,                             |
|                                          | a user with an unusable password cannot log in properly to the platform if the                                                           |
|                                          | ``common.djangoapps.third_party.pipeline.set_logged_in_cookies`` step is enabled.                                                        |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| ensure_user_has_profile                  | Create an empty profile object if the user does not have one.                                                                            |
|                                          | It can be used with the user_details_force_sync function to fill the profile after creation.                                             |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| force_user_post_save_callback            | Send the signal post_save to force the execution of user_post_save_callback,                                                             |
|                                          | this allows automatic enrollments if a third-party auth registers a user.                                                                |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| check_disconnect_pipeline_enabled        | Check whether disconnection from the auth provider is enabled or not. That's done checking for                                           |
|                                          | `disableDisconnectPipeline` setting, defined in the provider configuration.                                                              |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| assert_user_information                  | This pipeline function checks whether the user information from the LMS matches the information returned by the provider.                |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| create_signup_source_for_new_association | Register a new signup source for users with a new social auth link. The signup source will be associated with the current site and user. |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+
| ensure_user_has_signup_source            | Register a new signup source for users with a social auth link but no signup source associated with the current site.                    |
|                                          | The signup source will be associated with the current site and user.                                                                     |
+------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------+

You can visit the `file implementation <https://github.com/eduNEXT/eox-core/blob/dcoa/improve-docs/eox_core/pipeline.py>`_ for a better understanding.

Use the pipelines adding them in the LMS setting:

.. code-block::

  SOCIAL_AUTH_CONFIG_BASED_OPENIDCONNECT_PIPELINE = [
    ...,
    "eox_core.pipeline.ensure_user_has_profile",
    ...
  ]
