""" Backend test abstraction. """


def get_configuration_helper():
    """ Backend to get the configuration helper. """
    try:
        from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers  # pylint: disable=import-outside-toplevel
    except ImportError:
        configuration_helpers = object
    return configuration_helpers
