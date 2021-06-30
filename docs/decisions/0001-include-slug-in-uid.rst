1. Include a slug in the UID returned by the IdP
------------------------------------------------

Status
------
Accepted

Context
-------
Users that opt to authenticate using social authentication would have an association between the user in the platform
and the id given by the IdP. In a multi tenancy context there *will* be the case that multiple sites may use the same
Provider making unfeasible to identify site ownership from each association.

Decision
--------
A rather simple solution was already present in the saml backend, which prepends the slug to de uid. Therefore we have
decided to do the same for the other providers.

The design
===========
We alter the ``get_user_id`` function from the generic OIDC backend to return a modified version of the uid that includes
the slug in the format ``slug:uid``. The slug is obtained from the provider configuration and must be set under the
``Other Settings`` field, as this is the only field the backend can access directly besides ID and Secret.
All new associations will be correctly namespaced with the given slug. For existing associations the new
``get_user_id`` will fetch the corresponding association for the original uid updating the record in the
database with the new uid. The rest of the flow will be the same.

Through the configuration values ``SOCIAL_AUTH_NAMESPACED_UIDS``, ``SOCIAL_AUTH_ALLOW_SLUGLESS_UID`` and
``SOCIAL_AUTH_ALLOW_WRITE_SLUG_UID`` one can chose to enable the feature, forbid the use of the old format
and update the previous associations to the new format at login time respectively.

This changes will have to eventually be applied to other backends in the future.

Rejected alternatives
---------------------
1.
  - Create a new pipeline step to obtain the provider name and include it in the ``extra_data`` field of ``usersocialauth``.
  - Modify the admin view to include the slug from ``extra_data``

  The ``extra_data`` field can be easily ignored, that's not the case of ``uid`` where is possible to apply some
  restrictions for ids that don't follow the new format.
