""" Backend abstraction. """
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers  # pylint: disable=import-error


def get_configuration_helper():
    """ Backend to get the configuration helper. """
    return configuration_helpers
