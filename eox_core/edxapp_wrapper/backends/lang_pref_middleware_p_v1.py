"""
LanguagePreferenceMiddleware Backend.
"""
from openedx.core.djangoapps.lang_pref.middleware import LanguagePreferenceMiddleware  # pylint: disable=import-error


def get_language_preference_middleware():
    """Backend to get the LanguagePreferenceMiddleware from openedx."""
    return LanguagePreferenceMiddleware
