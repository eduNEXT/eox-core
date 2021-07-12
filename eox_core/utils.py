#!/usr/bin/python
"""
Util function definitions.
"""
import datetime
import hashlib

from django.conf import settings
from django.core import cache
from pytz import UTC
from rest_framework import serializers

from eox_core.edxapp_wrapper.users import get_user_profile

UserProfile = get_user_profile()

try:
    cache = cache.caches['general']  # pylint: disable=invalid-name
except Exception:  # pylint: disable=broad-except
    cache = cache.cache  # pylint: disable=invalid-name


def fasthash(string):
    """
    Hashes `string` into a string representation of a 128-bit digest.
    """
    md4 = hashlib.new("md4")
    md4.update(string.encode('utf-8'))
    return md4.hexdigest()


def get_valid_years():
    """
    Return valid list of year range, for the YEAR_OF_BIRTH_CHOICES
    constant.
    """
    current_year = datetime.datetime.now(UTC).year
    return list(range(current_year, current_year - 120, -1))


def get_gender_choices():
    """
    Try to return the valid options for the UserProfile field "gender"
    """
    return getattr(UserProfile, "GENDER_CHOICES", ())


def get_level_of_education_choices():
    """
    Try to return the valid options for the UserProfile field "level_of_education".
    """
    return getattr(UserProfile, "LEVEL_OF_EDUCATION_CHOICES", ())


def set_custom_field_restrictions(custom_field, serializer_field):
    """
    Given a custom_field definition dict, check for any
    restriction and add it to the serializer field dictionary

    This function is only called for custom fields of type
    "text". The allowed restrictions are taken from the platform's
    ALLOWED_RESTRICTIONS dictionary

    ALLOWED_RESTRICTIONS = {
        "text": ["min_length", "max_length"],
        "password": ["min_length", "max_length", "min_upper", "min_lower",
                     "min_punctuation", "min_symbol", "min_numeric", "min_alphabetic"],
        "email": ["min_length", "max_length", "readonly"],
    }
    """
    for key, value in custom_field.get("restrictions", {}).items():
        try:
            ["min_length", "max_length"].index(key)
            serializer_field[key] = int(value)
        except ValueError:
            raise serializers.ValidationError({"restriction error": "{key}: {value}.\
            The restriction may not be valid or the value is not an integer".format(
                key=key,
                value=value,
            )})

    return serializer_field


def set_select_custom_field(custom_field, serializer_field):
    """
    Given a custom_field definition dict with type=='select',
    add its options and default value (if exists) to the serializer
    field dictionary.
    """
    field_name = custom_field.get("name")
    choices = custom_field.get("options", [])
    serializer_field["choices"] = choices
    default = custom_field.get("default")

    if default:
        try:
            choices.index(default)
            serializer_field["default"] = default
            # A field can not be both `required` and have a `default`
            serializer_field["required"] = False
        except ValueError:
            raise serializers.ValidationError({"{}".format(field_name): "The default value must be one of the options"})

    return serializer_field


def get_registration_extra_fields():
    """
    Return only the registration extra fields
    that are not hidden.
    These fields are the ones that will be taken into
    account to initialize the EdxappExtendedUserSerializer
    """
    registration_extra_fields = getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})

    return {key: value for key, value in registration_extra_fields.items() if value in ["required", "optional"]}


def create_user_profile(user):
    """
    Creates a Profile to a User.
    """
    if not hasattr(user, "profile"):
        UserProfile.objects.create(user=user)
