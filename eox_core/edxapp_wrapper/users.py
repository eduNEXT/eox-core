#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Users public function definitions
"""

from importlib import import_module

from django.conf import settings


def get_edxapp_user(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_edxapp_user(*args, **kwargs)


def create_edxapp_user(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.create_edxapp_user(*args, **kwargs)


def delete_edxapp_user(*args, **kwargs):
    """ Deletes the edxapp user """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.delete_edxapp_user(*args, **kwargs)


def get_user_read_only_serializer(*args, **kwargs):
    """ Gets the Open edX model UserProfile """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_read_only_serializer(*args, **kwargs)


def check_edxapp_account_conflicts(*args, **kwargs):
    """ Checks the db for accounts with the same email or password """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.check_edxapp_account_conflicts(*args, **kwargs)


def get_course_enrollment():
    """ Gets the CourseEnrollment model """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_enrollment()


def get_course_team_user(*args, **kwargs):
    """ Gets the course_team_user function """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_team_user(*args, **kwargs)


def get_user_signup_source():
    """ Gets the UserSignupSource model """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_signup_source()


def get_user_profile():
    """ Gets the UserProfile model """

    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_profile()


def get_username_max_length():
    """ Gets max length allowed for the username"""
    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)
    return backend.USERNAME_MAX_LENGTH


def generate_password(*args, **kwargs):
    """
    Runs the generate_password funcion of edx-platform used to generate
     a random password.
    """
    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)
    return backend.generate_password(*args, **kwargs)


def get_user_attribute():
    """ Gets the UserAttribute model """
    backend_function = settings.EOX_CORE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_attribute()
