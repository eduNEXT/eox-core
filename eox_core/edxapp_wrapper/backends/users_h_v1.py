#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
from __future__ import absolute_import, unicode_literals

import logging

from copy import deepcopy
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from rest_framework.exceptions import APIException

from openedx.core.djangoapps.lang_pref import (  # pylint: disable=import-error
    LANGUAGE_KEY
)
from openedx.core.djangoapps.user_api.accounts.api import (  # pylint: disable=import-error
    check_account_exists
)
from openedx.core.djangoapps.user_api.accounts.serializers import (   # pylint: disable=import-error
    UserReadOnlySerializer
)
from openedx.core.djangoapps.user_api.preferences import api as preferences_api  # pylint: disable=import-error
from student.forms import AccountCreationForm  # pylint: disable=import-error
from student.helpers import (  # pylint: disable=import-error
    create_or_set_user_attribute_created_on_site
)
from student.views import create_account_with_params  # pylint: disable=import-error
from student.models import CourseEnrollment  # pylint: disable=import-error
from student.models import (UserAttribute, UserSignupSource,  # pylint: disable=import-error
                            create_comments_service_user)

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
        'extended_profile_fields': {
            'internal_id': '12',
            ...
        },
        'year_of_birth': '1981',
        'city': 'Boston',
        'verify_account_email': True,
        'enable_comments_service': True
    }
    user = create_edxapp_user(**data)

    """
    errors = []
    email = kwargs.pop("email")
    username = kwargs.pop("username")
    conflicts = check_edxapp_account_conflicts(email=email, username=username)
    if conflicts:
        return None, ["Fatal: account collition with the provided: {}".format(", ".join(conflicts))]
    request = kwargs.pop("request", False)
    request.data['name'] = kwargs.pop("fullname")
    # Get additional settings for this user
    email_validation = request.data.pop("verify_account_email", False)
    terms_of_service = request.data.pop("terms_of_service", None)
    honor_code = request.data.pop("honor_code", None)
    comments_service = request.data.pop("enable_comments_service", None)
    extended_profile_data = request.data.pop("extended_profile_fields", {})

    # Settings to be monkey patched to suit request
    registration_fields = getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})
    site_configuration = configuration_helpers.get_current_site_configuration()
    # Backup copies of original configurations
    _original_settings_features = deepcopy(settings.FEATURES)
    _original_settings_registration_fields = deepcopy(registration_fields)

    settings.FEATURES['SKIP_EMAIL_VALIDATION'] = not email_validation

    if not comments_service:
        if 'ENABLE_DISCUSSION_SERVICE' in settings.FEATURES:
            settings.FEATURES['ENABLE_DISCUSSION_SERVICE'] = False

    if terms_of_service:
        registration_fields['terms_of_service'] = 'required'
    else:
        registration_fields['terms_of_service'] = 'hidden'

    if honor_code:
        registration_fields['honor_code'] = 'required'
    else:
        registration_fields['honor_code'] = 'hidden'

    extended_profile_fields = {
        'extended_profile_fields': {key: '' for key in extended_profile_data}
        }
    site_configuration.values.update(extended_profile_fields)
    request.data.update(extended_profile_data)
    user = create_account_with_params(request, request.data)

    settings.FEATURES = _original_settings_features
    registration_fields = _original_settings_registration_fields
    #TODO restore site configuration

    if kwargs.pop("activate_user", False):
        user.is_active = True
        user.save()
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
