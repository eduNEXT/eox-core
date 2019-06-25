""" Backend abstraction. """

from microsite_configuration import microsite  # pylint: disable=import-error, no-name-in-module


def get_microsite():
    """ Backend to get the microsite. """
    return microsite
