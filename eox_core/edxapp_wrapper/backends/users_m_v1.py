#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/lilac.master tag
"""
import logging

from common.djangoapps.student.helpers import (  # pylint: disable=import-error,no-name-in-module
    create_or_set_user_attribute_created_on_site,
    do_create_account,
)
from common.djangoapps.student.models import (  # pylint: disable=import-error,no-name-in-module
    CourseEnrollment,
    LoginFailures,
    Registration,
    UserAttribute,
    UserProfile,
    UserSignupSource,
    create_comments_service_user,
    email_exists_or_retired,
    get_retired_email_by_email,
    username_exists_or_retired,
)
from crum import get_current_user
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from edx_django_utils.user import generate_password  # pylint: disable=import-error,unused-import
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY  # pylint: disable=import-error
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.accounts import USERNAME_MAX_LENGTH  # pylint: disable=import-error,unused-import
from openedx.core.djangoapps.user_api.accounts.serializers import UserReadOnlySerializer  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.accounts.views import \
    _set_unusable_password  # pylint: disable=import-error,unused-import
from openedx.core.djangoapps.user_api.models import UserRetirementStatus  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.preferences import api as preferences_api  # pylint: disable=import-error
from openedx.core.djangoapps.user_authn.views.register import \
    REGISTER_USER as post_register  # pylint: disable=import-error
from openedx.core.djangoapps.user_authn.views.registration_form import (  # pylint: disable=import-error
    AccountCreationForm,
    get_registration_extension_form,
)
from openedx.core.djangolib.oauth2_retirement_utils import \
    retire_dot_oauth2_models  # pylint: disable=import-error,unused-import
from openedx_events.learning.data import UserData, UserPersonalData  # pylint: disable=import-error
from openedx_events.learning.signals import STUDENT_REGISTRATION_COMPLETED  # pylint: disable=import-error
from rest_framework import status
from rest_framework.exceptions import NotFound
from social_django.models import UserSocialAuth  # pylint: disable=import-error

LOG = logging.getLogger(__name__)
User = get_user_model()  # pylint: disable=invalid-name


def get_user_read_only_serializer():
    """
    Great serializer that fits our needs
    """
    return UserReadOnlySerializer


def check_edxapp_account_conflicts(email, username):
    """
    Exposed function to check conflicts
    """
    conflicts = []

    if username and username_exists_or_retired(username):
        conflicts.append("username")

    if email and email_exists_or_retired(email):
        conflicts.append("email")

    return conflicts


def is_allowed_to_skip_extra_registration_fields(account_creation_data):
    """
    Returns True if the conditions are met to skip sending the extra
    registrations fields durint the account creation.

    Three conditions are checked in order to be able to skip
    these registration fields:
    1. The skip_extra_registration_fields field is sent in the data
        for the account creation as True.
    2. The user making the request is staff.
    3. The data received in the parameters does not contain any of the
        REGISTRATION_EXTRA_FIELDS configured for the microsite.

    In case any of these conditions is not met then the function returns
    False.
    """
    skip_extra_registration_fields = account_creation_data.pop("skip_extra_registration_fields", False)
    current_user = get_current_user()
    extra_fields = getattr(settings, "REGISTRATION_EXTRA_FIELDS", {})
    extended_profile_fields = getattr(settings, "extended_profile_fields", [])

    if not (skip_extra_registration_fields and current_user.is_staff):
        return False

    for field in account_creation_data.keys():
        if field in extra_fields.keys() or field in extended_profile_fields:
            return False

    return True


class EdnxAccountCreationForm(AccountCreationForm):
    """
    A form to extend the behaviour of the AccountCreationForm.
    For now the purpose of this form is to allow to make the
    password optional if the flag 'skip_password' is True.
    This form it's currently only used for validation, not rendering.
    """

    def __init__(  # pylint:disable=too-many-arguments
            self,
            data=None,
            extra_fields=None,
            extended_profile_fields=None,
            do_third_party_auth=True,
            tos_required=True,
    ):
        super().__init__(
            data=data,
            extra_fields=extra_fields,
            extended_profile_fields=extended_profile_fields,
            do_third_party_auth=do_third_party_auth,
            tos_required=tos_required,
        )

        if data.pop("skip_password", False):
            self.fields['password'] = forms.CharField(required=False)


def create_edxapp_user(*args, **kwargs):
    """
    Creates a user on the open edx django site using calls to
    functions defined in the edx-platform codebase

    Example call:

    data = {
        'email': "address@example.org",
        'username': "Username",
        'password': "P4ssW0rd",
        'fullname': "Full Name",
        'activate': True,
        'site': request.site,
        'language_preference': 'es-419',
    }
    user = create_edxapp_user(**data)

    """
    errors = []

    kwargs["name"] = kwargs.pop("fullname", None)
    email = kwargs.get("email")
    username = kwargs.get("username")
    conflicts = check_edxapp_account_conflicts(email=email, username=username)
    if conflicts:
        return None, [f"Fatal: account collition with the provided: {', '.join(conflicts)}"]

    account_creation_form_data = {
        "data": kwargs,
        "tos_required": False,
        # "enforce_password_policy": enforce_password_policy,
    }

    # Check if we should send the extra registration fields
    if not is_allowed_to_skip_extra_registration_fields(kwargs):
        account_creation_form_data["extra_fields"] = getattr(settings, "REGISTRATION_EXTRA_FIELDS", {})
        account_creation_form_data["extended_profile_fields"] = getattr(settings, "extended_profile_fields", [])

    # Go ahead and create the new user
    with transaction.atomic():
        # Is possible to extend the registration form with a custom app
        # An example form app for this can be found at http://github.com/open-craft/custom-form-app
        custom_form = get_registration_extension_form(data=account_creation_form_data["data"])
        # if not form:
        form = EdnxAccountCreationForm(**account_creation_form_data)
        (user, profile, registration) = do_create_account(form, custom_form)  # pylint: disable=unused-variable

    site = kwargs.pop("site", False)
    if site:
        create_or_set_user_attribute_created_on_site(user, site)
    else:
        errors.append("The user was not assigned to any site")

    try:
        create_comments_service_user(user)
    except Exception:  # pylint: disable=broad-except
        errors.append("No comments_service_user was created")

    # TODO: link account with third party auth

    # Announce registration through API call
    post_register.send_robust(sender=None, user=user)  # pylint: disable=no-member

    STUDENT_REGISTRATION_COMPLETED.send_event(
        user=UserData(
            pii=UserPersonalData(
                username=user.username,
                email=user.email,
                name=user.profile.name,  # pylint: disable=no-member
            ),
            id=user.id,
            is_active=user.is_active,
        ),
    )

    lang_pref = kwargs.pop("language_preference", False)
    if lang_pref:
        try:
            preferences_api.set_user_preference(user, LANGUAGE_KEY, lang_pref)
        except Exception:  # pylint: disable=broad-except
            errors.append(f"Could not set lang preference '{lang_pref}' for user '{user.username}'")

    if kwargs.pop("activate_user", False):
        user.is_active = True
        user.save()

    # TODO: run conditional email sequence

    return user, errors


def get_edxapp_user(**kwargs):
    """
    Retrieve a user by username and/or email

    The user will be returned only if it belongs to the calling site

    Examples:
        >>> get_edxapp_user(
            {
                "username": "Bob",
                "site": request.site
            }
        )
        >>> get_edxapp_user(
            {
                "email": "Bob@mailserver.com",
                "site": request.site
            }
        )
    """
    params = {key: kwargs.get(key) for key in ['username', 'email'] if key in kwargs}
    site = kwargs.get('site')
    try:
        domain = site.domain
    except AttributeError:
        domain = None

    try:
        user = User.objects.get(**params)
        for source_method in FetchUserSiteSources.get_enabled_source_methods():
            if source_method(user, domain):
                break
        else:
            raise User.DoesNotExist
    except User.DoesNotExist:
        raise NotFound(f'No user found by {str(params)} on site {domain}.') from User.DoesNotExist
    return user


def delete_edxapp_user(*args, **kwargs):
    """
    Deletes a user from the platform.
    """
    msg = None

    user = kwargs.get("user")
    case_id = kwargs.get("case_id")
    site = kwargs.get("site")
    is_support_user = kwargs.get("is_support_user")

    user_response = f"The user {user.username} <{user.email}> "

    signup_sources = user.usersignupsource_set.all()
    sources = [signup_source.site for signup_source in signup_sources]

    if site and site.name.upper() in (source.upper() for source in sources):
        if len(sources) == 1:
            with transaction.atomic():
                support_label = "_support" if is_support_user else ""
                user.email = f"{user.email}{case_id}.ednx{support_label}_retired"
                user.save()

                # Add user to retirement queue.
                UserRetirementStatus.create_retirement(user)

                # Unlink LMS social auth accounts
                UserSocialAuth.objects.filter(user_id=user.id).delete()

                # Change LMS password & email
                user.email = get_retired_email_by_email(user.email)
                user.save()
                _set_unusable_password(user)

                # Remove the activation keys sent by email to the user for account activation.
                Registration.objects.filter(user=user).delete()

                # Delete OAuth tokens associated with the user.
                retire_dot_oauth2_models(user)

                # Delete user signup source object
                signup_sources[0].delete()

                msg = f"{user_response} has been removed"
        else:
            for signup_source in signup_sources:
                if signup_source.site.upper() == site.name.upper():
                    signup_source.delete()

                    msg = f"{user_response} has more than one signup source. The signup source from the site {site} has been deleted"

        return msg, status.HTTP_200_OK

    raise NotFound(f"{user_response} does not have a signup source on the site {site}")


def get_course_team_user(*args, **kwargs):
    """
    Get _course_team_user function.
    We need to check if the SERVICE_VARIANT is equal to cms, since
    contentstore is a module registered in the INSTALLED_APPS
    of the cms only.
    """
    if settings.SERVICE_VARIANT == 'cms':
        from contentstore.views.user import _course_team_user  # pylint: disable=import-error,import-outside-toplevel
        return _course_team_user(*args, **kwargs)
    return None


class FetchUserSiteSources:
    """
    Methods to make the comparison to check if an user belongs to a site plus the
    get_enabled_source_methods that just brings an array of functions enabled to do so
    """

    @classmethod
    def get_enabled_source_methods(cls):
        """ Brings the array of methods to check if an user belongs to a site. """
        sources = configuration_helpers.get_value(
            'EOX_CORE_USER_ORIGIN_SITE_SOURCES',
            getattr(settings, 'EOX_CORE_USER_ORIGIN_SITE_SOURCES')
        )
        return [getattr(cls, source) for source in sources]

    @staticmethod
    def fetch_from_created_on_site_prop(user, domain):
        """ Fetch option. """
        if not domain:
            return False
        return UserAttribute.get_user_attribute(user, 'created_on_site') == domain

    @staticmethod
    def fetch_from_user_signup_source(user, domain):
        """ Read the signup source. """
        return len(UserSignupSource.objects.filter(user=user, site=domain)) > 0

    @staticmethod
    def fetch_from_unfiltered_table(user, site):
        """ Fetch option that does not take into account the multi-tentancy model of the installation. """
        return bool(user)


def get_course_enrollment():
    """ get CourseEnrollment model """
    return CourseEnrollment


def get_user_signup_source():
    """ get UserSignupSource model """
    return UserSignupSource


def get_login_failures():
    """ get LoginFailures model """
    return LoginFailures


def get_user_profile():
    """ Gets the UserProfile model """

    return UserProfile


def get_user_attribute():
    """ Gets the UserAttribute model """
    return UserAttribute
