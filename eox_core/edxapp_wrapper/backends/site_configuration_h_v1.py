"""
Backend for site configurations.
"""

from openedx.core.djangoapps.site_configuration.helpers import get_all_orgs  # pylint: disable=import-error


def get_all_orgs_helper():
    """ get get_all_orgs helper function. """
    return get_all_orgs()
