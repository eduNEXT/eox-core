"""
Contains all the forms required by the API

    - EdnxExtendedAccountCreationForm: Allows to create
    an edxapp user with all the ednx_custom_regitration_fields
"""
from django import forms
from django.conf import settings
from django.core.validators import ValidationError

from openedx.core.djangoapps.user_authn.views.registration_form import (  # pylint: disable=import-error
    AccountCreationForm,
)

ACCOUNT_CREATION_FIELDS_OPTIONS = {}


def validate_option(value, field_name):
    """
    Validates a given value is a correct
    option for a select field.
    """
    if value not in ACCOUNT_CREATION_FIELDS_OPTIONS[field_name]:
        raise ValidationError(
            '{} is not a valid option'.format(value)
        )


class EdnxExtendedAccountCreationForm(AccountCreationForm):
    """
    A form for extended account creation data, including
    all of the ednx_custom_regitration_fields.

    It is currently only used for validation, not rendering.
    """

    def __init__(
            self,
            data=None,
            extra_fields=None,
            extended_profile_fields=None,
            tos_required=False,
    ):
        extra_fields.pop('terms_of_service', None)

        super(EdnxExtendedAccountCreationForm, self).__init__(
            data=data,
            extra_fields=extra_fields,
            extended_profile_fields=extended_profile_fields,
            tos_required=tos_required,
        )

        ednx_custom_regitration_fields = getattr(settings, 'EDNX_CUSTOM_REGISTRATION_FIELDS', {})

        for custom_field in ednx_custom_regitration_fields:

            field_name = custom_field.get("name")
            if field_name in self.extended_profile_fields:

                required = extra_fields.get(field_name) == "required"
                field_type = custom_field.get("type")

                if field_type in ["select", "checkbox"]:
                    ACCOUNT_CREATION_FIELDS_OPTIONS[field_name] = custom_field.get("options", [])
                    value = data[field_name]

                    self.fields[field_name] = forms.CharField(
                        required=required,
                        validators=[validate_option(value, field_name)],
                        error_messages={
                            "required": "{} is required".format(field_name),
                        }
                    )

                else:
                    restrictions = extra_fields.get("restrictions", {})
                    min_length = restrictions.get("min_length")
                    max_length = restrictions.get("max_length")

                    self.fields[field_name] = forms.CharField(
                        required=required,
                        min_length=min_length,
                        max_length=max_length,
                        error_messages={
                            "required": "{} is required".format(field_name),
                            "min_length": "The min lenght is {}".format(min_length),
                            "max_length": "The max lenght is {}".format(min_length),
                        }
                    )
