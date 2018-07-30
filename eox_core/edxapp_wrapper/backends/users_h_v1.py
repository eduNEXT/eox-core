#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
import logging

from django.db import transaction
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
from student.forms import AccountCreationForm  # pylint: disable=import-error
from student.helpers import do_create_account, create_or_set_user_attribute_created_on_site  # pylint: disable=import-error
from student.models import create_comments_service_user  # pylint: disable=import-error

LOG = logging.getLogger(__name__)


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
        'site': request.site
    }
    user = create_edxapp_user(**data)

    """
    errors = []


    email = kwargs.pop("email")
    username = kwargs.pop("username")
    conflicts = check_account_exists(email=email, username=username)
    if conflicts:
        for field in conflicts:
            errors.append("There is already an account using this {} field".format(field))

        return {
            "errors": errors,
        }


    password = kwargs.pop("password")
    fullname = kwargs.pop("fullname")
    data = {
        'username': username,
        'email': email,
        'password': password,
        'name': fullname,
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
    except Exception as e:
        errors.append("No comments_service_user was created")


    # TODO: link account with third party auth


    lang_pref = kwargs.pop("language_preference", False):
    if lang_pref:
        try:
            preferences_api.set_user_preference(user, LANGUAGE_KEY, lang_pref)
        except Exception as e:
            errors.append("Could not set lang preference '{} for user '{}'".format(
                lang_pref,
                user.username,
            ))


    if kwargs.pop("activate", False):
        user.is_active = True
        user.save()


    # TODO: run conditional email sequence

    return user, errors
