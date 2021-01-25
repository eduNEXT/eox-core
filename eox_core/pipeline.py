"""
The pipeline module defines functions that are used in the third party authentication flow
"""
import logging

from django.db.models.signals import post_save

from eox_core.edxapp_wrapper.users import get_user_profile

try:
    from social_core.exceptions import AuthFailed, NotAllowedToDisconnect
except ImportError:
    AuthFailed = object
    NotAllowedToDisconnect = object

LOG = logging.getLogger(__name__)


# pylint: disable=unused-argument,keyword-arg-before-vararg
def ensure_user_has_profile(backend, details, user=None, *args, **kwargs):
    """
    This pipeline function creates an empty profile object if the user does not have one.
    It can be used with the user_details_force_sync function to fill the profile after creation.
    """
    if user:
        user_profile_model = get_user_profile()
        try:
            __ = user.profile
        except user_profile_model.DoesNotExist:
            user_profile_model.objects.create(user=user)
            LOG.info('Created new profile for user during the third party pipeline: "%s"', user)


def force_user_post_save_callback(auth_entry, is_new, user=None, *args, **kwargs):
    """
    Send the signal post_save in order to force the execution of user_post_save_callback, see it in
    https://github.com/eduNEXT/edunext-platform/blob/4169327231de00991c46b6192327fe50b0406561/common/djangoapps/student/models.py#L652
    this allows the automatic enrollments if a user is registered by a third party auth.
    This depends on "third_party_auth.pipeline.parse_query_params".

    the discussion left three options:

    1)
        user._changed_fields = {'is_active': user.is_active}  # pylint: disable=protected-access
        post_save.send_robust(
            sender=user.__class__,
            instance=user,
            created=False
        )

    2)
        user.is_active = False
        user.save()
        user.is_active = True
        user.save()

    3)
        registration = Registration.objects.get_or_create(user=user)
        user.is_active = False
        user.save()
        registration.activate()

    The first one was selected because the second executed multiple unnecessary process and third one
    needs to implement a new backend.
    """
    if auth_entry == 'register' and user and is_new:
        user._changed_fields = {'is_active': user.is_active}  # pylint: disable=protected-access
        post_save.send_robust(
            sender=user.__class__,
            instance=user,
            created=False
        )


def check_disconnect_pipeline_enabled(backend, *args, **kwargs):
    """
    This pipeline function checks whether disconnection from the auth provider is enabled or not. That's
    done checking for `disableDisconnectPipeline` setting defined in the provider configuration.

    For example:
        To avoid disconnection from SAML, add the following to `Other config str` in your SAMLConfiguration:

        "BACKEND_OPTIONS": { "disableDisconnectPipeline":true },

        Now, to avoid disconnection from an Oauth2Provider, add the same setting to `Other settings` in your
        Oauth2Provider.

    It's recommended to place this function at the beginning of the pipeline.
    """
    if backend and backend.setting("BACKEND_OPTIONS", {}).get("disableDisconnectPipeline"):
        LOG.exception("Disconnection pipeline is disabled, users are not allowed to disconnect.")
        raise NotAllowedToDisconnect()  # pylint: disable=raising-non-exception


def assert_user_information(details, user, backend, *args, **kwargs):
    """
    This pipeline function checks whether the user information from the LMS matches the information
    returned by the provider.

    For example:
        To avoid connection when the user's email from the LMS differs from the email returned by the provider,
        add the setting:

        "BACKEND_OPTIONS": { "assertUserInformationMatchFields":["email",...] }

    It's recommended to place this step after the user is available (ie. after ensure_user_information step) and
    before user association (ie. before user_association step)
    """
    if not (user and backend):
        return

    defined_fields = backend.setting("BACKEND_OPTIONS", {}).get("assertUserInformationMatchFields", [])

    for field in defined_fields:

        if str(details.get(field, "")) != str(getattr(user, field, "")):
            LOG.exception(
                "Credentials not allowed: field %s returned by provider does not match with the user %s information.",
                field,
                user.username,
            )
            raise AuthFailed(backend, "Credentials not allowed.")  # pylint: disable=raising-non-exception
