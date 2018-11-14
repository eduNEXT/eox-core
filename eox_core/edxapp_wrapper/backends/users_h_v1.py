#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
from __future__ import absolute_import, unicode_literals
import logging

from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import APIException
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.preferences import api as preferences_api  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.accounts.serializers import UserReadOnlySerializer  # pylint: disable=import-error
from student.forms import AccountCreationForm  # pylint: disable=import-error
from student.helpers import do_create_account, create_or_set_user_attribute_created_on_site  # pylint: disable=import-error
from student.models import create_comments_service_user, UserAttribute, UserSignupSource, CourseEnrollment  # pylint: disable=import-error

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


def get_edxapp_user(**kwargs):
    """
    Retrieve an user by username and/or email
    """
    params = {key: kwargs.get(key) for key in ['username', 'email'] if key in kwargs}
    site = kwargs.get('site')

    try:
        user = User.objects.get(**params)
        for source_method in FetchUserSiteSources.get_enabled_source_methods():
            if source_method(user, site.domain):
                break
        else:
            raise User.DoesNotExist
    except User.DoesNotExist:
        raise APIException('No user found by {query} on site {site}.'.format(query=str(params), site=site.domain))
    return user


class FetchUserSiteSources(object):
    """
    Methods to make the comparison to check if an user belongs to a site plus the
    get_enabled_source_methods that just brings an array of functions enabled to do so
    """

    ALL_SOURCES = ['fetch_from_created_on_site_prop', 'fetch_from_user_signup_source']

    @classmethod
    def get_enabled_source_methods(cls):
        """ brings the array of methods to check if an user belongs to a site """
        sources = getattr(settings, 'EOX_CORE_USER_ORIGIN_SITE_SOURCES', cls.ALL_SOURCES)
        return [getattr(cls, source) for source in sources]

    @staticmethod
    def fetch_from_created_on_site_prop(user, site):
        """ fetch option """
        return UserAttribute.get_user_attribute(user, 'created_on_site') == site

    @staticmethod
    def fetch_from_user_signup_source(user, site):
        """ fetch option """
        return len(UserSignupSource.objects.filter(user=user, site=site)) > 0


def get_course_enrollment():
    """ get CourseEnrollment model """
    return CourseEnrollment
