#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from openedx.core.djangoapps.lang_pref import (  # pylint: disable=import-error
    LANGUAGE_KEY
)
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.accounts.api import (  # pylint: disable=import-error
    check_account_exists,
    update_account_settings,
)
from openedx.core.djangoapps.user_api.accounts.serializers import UserReadOnlySerializer  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.errors import (  # pylint: disable=import-error
    AccountUpdateError,
    AccountValidationError,
)
from openedx.core.djangoapps.user_api.preferences import api as preferences_api  # pylint: disable=import-error
from student.forms import AccountCreationForm  # pylint: disable=import-error
from student.helpers import (  # pylint: disable=import-error
    create_or_set_user_attribute_created_on_site,
    do_create_account,
)
from student.models import (  # pylint: disable=import-error
    CourseEnrollment,
    create_comments_service_user,
    email_exists_or_retired,
    LoginFailures,
    UserAttribute,
    UserSignupSource,
)
# pylint: disable=import-error
from util.password_policy_validators import validate_password  # pylint: disable=no-name-in-module

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
    return check_account_exists(email=email, username=username)


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

    email = kwargs.pop("email")
    username = kwargs.pop("username")
    conflicts = check_edxapp_account_conflicts(email=email, username=username)
    if conflicts:
        return None, ["Fatal: account collition with the provided: {}".format(", ".join(conflicts))]

    data = {
        'username': username,
        'email': email,
        'password': kwargs.pop("password"),
        'name': kwargs.pop("fullname"),
    }
    # Go ahead and create the new user
    with transaction.atomic():
        # In theory is possible to extend the registration form with a custom app
        # An example form app for this can be found at http://github.com/open-craft/custom-form-app
        # form = get_registration_extension_form(data=params)
        # if not form:
        form = AccountCreationForm(
            data=data,
            tos_required=False,
            # TODO: we need to support the extra profile fields as defined in the django.settings
            # extra_fields=extra_fields,
            # extended_profile_fields=extended_profile_fields,
            # enforce_password_policy=enforce_password_policy,
        )
        (user, profile, registration) = do_create_account(form)  # pylint: disable=unused-variable

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

    lang_pref = kwargs.pop("language_preference", False)
    if lang_pref:
        try:
            preferences_api.set_user_preference(user, LANGUAGE_KEY, lang_pref)
        except Exception:  # pylint: disable=broad-except
            errors.append("Could not set lang preference '{} for user '{}'".format(
                lang_pref,
                user.username,
            ))

    if kwargs.pop("activate_user", False):
        user.is_active = True
        user.save()

    # TODO: run conditional email sequence

    return user, errors


def update_edxapp_user(user, **kwargs):
    """
    Update a user on the open edx django site using calls to
    functions defined in the edx-platform codebase.

    Example call:

    data: A JSON containing the username and key-value pairs of the fields to be updated.

    data = {
        'username': "Username",
        'email': "address@example.org",
        'name': "Full Name",
        'gender': 'f',
        'bio': '...',
        'force': true,
        'reason': '...',
    }
    user = update_edxapp_user(**data)

    """
    try:
        update_fields = kwargs
        force = kwargs.pop('force', False)
        new_email = update_fields.pop('email', None)
        new_password = update_fields.pop('password', None)

        # Only update configured extended profile fields
        if 'extended_profile' in update_fields:
            extended_profile_field_names = configuration_helpers.get_value('extended_profile_fields', [])
            for field in update_fields['extended_profile']:
                if field['field_name'] not in extended_profile_field_names:
                    raise ValidationError('Invalid extended profile field {}'.format(field['field_name']))

        # Update the email and password of the user only if it's explicitly
        # requested by setting the force param to true. A reason for the change must be given.
        if force:
            if new_email and not email_exists_or_retired(new_email):
                user.email = new_email

            # Explicit checking that the password is not None, because an empty password
            # could be valid and should be validated
            if new_password is not None and validate_password(new_password, user=user) is None:
                user.set_password(new_password)

        update_account_settings(requesting_user=user, update=update_fields)
        user.save()

    except (AccountValidationError, AccountUpdateError) as exp:
        errors = []

        if hasattr(exp, 'field_errors'):
            for error in exp.field_errors:
                err_msg = exp.field_errors[error]['user_message'] if 'user_message' in exp.field_errors[error] else 'Field error'
                errors.append("{}:{}".format(error, err_msg))
            raise ValidationError(errors)
        else:
            raise NotFound("Error: the update could not be processed, please review your request ")
    except DjangoValidationError as exp:
        raise ValidationError(exp.message)

    return user


def delete_edxapp_user(user):
    """
    Delete a user.

    To delete a user we're deactivating in the platform,
    so it no longer has access however no user
    data is deleted, this is just the first step in
    the retirement pipeline (pending).
    """
    try:
        user.is_active = False
        retired_email = user.email
        retired_email = retired_email.replace(u'@', u'+')
        user.email = '{}@{}'.format(retired_email,
                                    settings.EOX_CORE_USER_EMAIL_RETIRED_SUFFIX)
        user.save()
    except Exception:  # pylint: disable=broad-except
        raise NotFound("The deletion could not be completed")


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
        raise NotFound('No user found by {query} on site {site}.'.format(query=str(params), site=domain))
    return user


def get_course_team_user(*args, **kwargs):
    """
    Get _course_team_user function.
    We need to check if the SERVICE_VARIANT is equal to cms, since
    contentstore is a module registered in the INSTALLED_APPS
    of the cms only.
    """
    if settings.SERVICE_VARIANT == 'cms':
        from contentstore.views.user import _course_team_user  # pylint: disable=import-error
        return _course_team_user(*args, **kwargs)
    return None


class FetchUserSiteSources(object):
    """
    Methods to make the comparison to check if an user belongs to a site plus the
    get_enabled_source_methods that just brings an array of functions enabled to do so
    """

    @classmethod
    def get_enabled_source_methods(cls):
        """ Brings the array of methods to check if an user belongs to a site. """
        sources = getattr(settings, 'EOX_CORE_USER_ORIGIN_SITE_SOURCES')
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
