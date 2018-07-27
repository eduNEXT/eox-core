#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
import logging

from django.db import transaction
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
from student.forms import AccountCreationForm  # pylint: disable=import-error
from student.helpers import do_create_account, create_or_set_user_attribute_created_on_site  # pylint: disable=import-error
from student.models import create_comments_service_user  # pylint: disable=import-error

LOG = logging.getLogger(__name__)


def create_edxapp_user(*args, **kwargs):

    errors = []

    email = kwargs.pop("email")
    username = kwargs.pop("username")
    password = kwargs.pop("password")
    fullname = kwargs.pop("fullname")
    site = kwargs.pop("site", False)


    conflicts = check_account_exists(email=email, username=username)
    if conflicts:
        raise Exception

    data = {
        'username': username,
        'email': email,
        'password': password,
        'name': fullname,
    }

    # Go ahead and create the new user
    with transaction.atomic():
        form = AccountCreationForm(
            data=data,
            tos_required=False,
            # extra_fields=extra_fields,
            # extended_profile_fields=extended_profile_fields,
            # enforce_password_policy=enforce_password_policy,
        )
        # custom_form = get_registration_extension_form(data=params)
        # TODO: use custom form
        (user, profile, registration) = do_create_account(form)  # pylint: disable=unused-variable

    if site:
        create_or_set_user_attribute_created_on_site(user, site)

    # create_comments_service_user(user)
    # TODO: link account with third party auth
    # TODO: preferences_api.set_user_preference(user, LANGUAGE_KEY, get_language())
    # TODO: run conditional email sequence

    return {
        "errors": errors,
        "username": user.username  # TODO: return a better representation
    }
