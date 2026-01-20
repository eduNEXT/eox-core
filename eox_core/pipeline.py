"""
The pipeline module defines functions that are used in the third party authentication flow
"""
import logging

from common.djangoapps.third_party_auth.pipeline import get_complete_url
from crum import get_current_request
from django.db.models.signals import post_save
from django.shortcuts import redirect
from openedx.core.djangoapps.lang_pref.helpers import get_language_cookie, set_language_cookie
from social_core.exceptions import AuthFailed, NotAllowedToDisconnect
from social_core.pipeline import partial

from eox_core.edxapp_wrapper.users import (
    generate_password,
    get_user_attribute,
    get_user_profile,
    get_user_signup_source,
)
from eox_core.logging import logging_pipeline_step

UserSignupSource = get_user_signup_source()  # pylint: disable=invalid-name
LOG = logging.getLogger(__name__)


# pylint: disable=unused-argument,keyword-arg-before-vararg
def ensure_new_user_has_usable_password(backend, user=None, **kwargs):
    """
    This pipeline function assigns an usable password to an user in case that the user has an unusable password on user cretion.
    At the creation of new users through some TPA providers, some of them are created with an unusable password, a user with an unusable password cannot login
    properly in the platform if the common.djangoapps.third_party.pipeline.set_logged_in_cookies step is enabled.

    See: https://github.com/eduNEXT/edunext-platform/blob/c83b82a4aba2a5496e3b7da83972a8edf25fcdd2/common/djangoapps/third_party_auth/pipeline.py#L673

    It's recommended to place this step after the social core step that creates the users: (social_core.pipeline.user.create_user).
    """
    is_new = kwargs.get('is_new')

    if user and is_new and not user.has_usable_password():
        user.set_password(generate_password(length=25))
        user.save()

        user_attribute_model = get_user_attribute()
        user_attribute_model.set_user_attribute(user, 'auto_password_via_tpa_pipeline', 'true')

        logging_pipeline_step(
            "info",
            "Assigned an usable password to the user on creation.",
            **locals()
        )


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
            logging_pipeline_step(
                "info",
                "Created new profile for user during the third party pipeline.",
                **locals()
            )


def force_user_post_save_callback(user=None, *args, **kwargs):
    """
    Send the signal post_save in order to force the execution of user_post_save_callback, see it in
    https://github.com/eduNEXT/edunext-platform/blob/4169327231de00991c46b6192327fe50b0406561/common/djangoapps/student/models.py#L652
    this allows the automatic enrollments if a user is registered by a third party auth.

    It's recommended to place this step after the social core step that creates the users: (social_core.pipeline.user.create_user).

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
    is_new = kwargs.get('is_new')

    if user and is_new:
        user._changed_fields = {'is_active': user.is_active}  # pylint: disable=protected-access
        post_save.send_robust(
            sender=user.__class__,
            instance=user,
            created=False
        )
        logging_pipeline_step(
            "info",
            "Post_save signal sent in order to force the execution of user_post_save_callback.",
            **locals()
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
        logging_pipeline_step(
            "error",
            "Disconnection pipeline is disabled, users are not allowed to disconnect.",
            **locals()
        )
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
            logging_pipeline_step(
                "error",
                f"Credentials not allowed: field {field} returned by provider does not match with the users information.",
                **locals()
            )
            raise AuthFailed(backend, "Credentials not allowed.")  # pylint: disable=raising-non-exception


def create_signup_source_for_new_association(user=None, *args, **kwargs):
    """
    This pipeline step registers a new signup source for users with new social auth link. The signup source
    will have associated the current site and user.

    It's recommended to place this step after the creation of the social auth link, i.e, after the step
    'social_core.pipeline.social_auth.associate_user',

    To avoid errors or unnecessary searches, these steps are skipped using 'is_new' key insterted by
    'social_core.pipeline.user.create_user' after creating a user.
    """
    if not user or kwargs.get("is_new", False):
        return

    if kwargs.get("new_association", False):
        _, created = UserSignupSource.objects.get_or_create(user=user, site=get_current_request().site)
        if created:
            logging_pipeline_step(
                "info",
                "Created new singup source for user during the third party pipeline.",
                **locals()
            )


def ensure_user_has_signup_source(user=None, *args, **kwargs):
    """
    This pipeline step registers a new signup source for users that have a social auth link but
    no signup source associated with the current site. The signup source will be associated to
    the current site and user.

    It's recommended to place this step at the end of the TPA pipeline, e.g., after the step
    'eox_core.pipeline.ensure_user_has_profile',

    To avoid errors or unnecessary searches, these steps are skipped using 'is_new' key insterted by
    'social_core.pipeline.user.create_user' after creating a user.
    """
    if not user or kwargs.get("is_new", False):
        return

    _, created = UserSignupSource.objects.get_or_create(user=user, site=get_current_request().site)
    if created:
        logging_pipeline_step(
            "info",
            "Created new singup source for user during the third party pipeline.",
            **locals()
        )


def map_language_to_openedx(lang: str) -> str:
    """
    Maps a BCP 47 language code to Open edX language format.
    """
    lang = lang.strip()

    mapping = {
        "en": "en",
        "es": "es-es",
        "pt": "pt-pt",
        "pt-BR": "pt-br",
        "de": "de-de",
        "pl": "pl",
        "ca": "ca",
    }

    return mapping.get(lang, "en")


def get_language_from_sso_provider(response: dict) -> str:
    """
    Get the language from the SSO provider.

    Args:
        response: The response from the SSO provider.

    Returns:
        The language from the SSO provider.
    """
    return map_language_to_openedx(response.get("language"))


# pylint: disable=unused-argument
@partial.partial
def set_language_preference_from_sso_provider(
    response,
    user=None,
    strategy=None,
    current_partial=None,
    **kwargs,
):
    """
    Set the language preference cookie from SSO provider data using a redirect pattern.

    This is a partial pipeline function that extracts the language code from SSO provider
    data and sets it as a language preference cookie. It uses the redirect pattern with
    @partial.partial decorator to set the cookie while maintaining the authentication flow.

    The function compares the current language cookie with the requested language and only
    performs a redirect if they differ, avoiding unnecessary redirects when the language
    is already set correctly.

    Args:
        *args: Additional positional arguments passed through the pipeline.
        user: The User object being authenticated. Must be present for language setting.
        strategy: The python-social-auth strategy instance containing the request object.
        current_partial: The current partial token containing backend information for
            generating the completion URL.
        **kwargs: Additional keyword arguments. Expected to contain:
            - language (str): The language code to set (e.g., 'es', 'en', 'pt-pt').

    Returns:
        HttpResponseRedirect: A redirect response with the language cookie set if the
            language differs from the current cookie and the redirect URL can be
            generated successfully.
        None: If the language matches the current cookie, user is not present, request
              is unavailable, or redirect URL generation fails.
    """
    print("[DEBUG] set_language_preference_from_sso_provider")
    print("\n\nResponse:", response)
    print("\n\nUser:", user)
    print("\n\nStrategy:", strategy)
    print("\n\nCurrent partial:", current_partial)
    print("\n\nkwargs:", kwargs)

    language = get_language_from_sso_provider(response)

    if language and user is not None:
        request = strategy.request if strategy else None

        if request is not None:
            current_cookie = get_language_cookie(request)

            if current_cookie != language:
                try:
                    redirect_url = get_complete_url(current_partial.backend)
                except ValueError:
                    pass
                else:
                    response = redirect(redirect_url)
                    set_language_cookie(request, response, language)
                    return response

    return None
