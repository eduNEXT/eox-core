"""
Extensions to the regular defined third party auth backends
"""
import logging

from django.conf import settings

try:
    from social_core.backends.open_id_connect import OpenIdConnectAuth
    from social_core.backends.oauth import BaseOAuth2
except ImportError:
    BaseOAuth2 = object
    OpenIdConnectAuth = object

from eox_core.edxapp_wrapper.configuration_helpers import get_configuration_helper


configuration_helper = get_configuration_helper()  # pylint: disable=invalid-name

LOG = logging.getLogger(__name__)


class ConfigurableOpenIdConnectAuth(OpenIdConnectAuth):
    """
    Generic backend that can be configured via the site settings
    """
    name = 'config-based-openidconnect'

    def __init__(self, *args, **kwargs):
        conf = configuration_helper.get_value(
            "OIDC_CONFIG",
            getattr(settings, 'OIDC_CONFIG', {})
        )

        for key in conf:
            try:
                setattr(self, key, conf.get(key, getattr(self, key)))
            except Exception:  # pylint: disable=broad-except
                LOG.error("Tried and failed to set property %s of a config-based-openidconnect", key)

        super(ConfigurableOpenIdConnectAuth, self).__init__(*args, **kwargs)


class ConfigurableOAuth2(BaseOAuth2):
    """Configurable OAuth2 class."""
    name = 'config-based-oauth2'
    USERNAME_KEY = 'username'
    FIRST_NAME_KEY = None
    LAST_NAME_KEY = None
    FULL_NAME_KEY = None
    EMAIL_KEY = 'email'
    RESPONSE_ATTRIBUTES_KEY = ''
    USER_DETAILS_URL = None

    def __init__(self, *args, **kwargs):
        """init."""
        conf = configuration_helper.get_value(
            'EOX_OAUTH2',
            getattr(settings, 'EOX_OAUTH2', {})
        )

        for key in conf:
            try:
                setattr(self, key, conf.get(key, getattr(self, key)))
            except Exception:  # pylint: disable=broad-except
                LOG.error("Tried and failed to set property %s of a configurable connect OAuth2", key)

        super(ConfigurableOAuth2, self).__init__(*args, **kwargs)

    def get_user_details(self, response):
        """Get user details."""
        details = response.get([self.RESPONSE_ATTRIBUTES_KEY], {})
        fullname, first_name, last_name = self.get_user_names(self._get_user_name_values(details))
        return {
            'username': details.get(self.USERNAME_KEY, ''),
            'email': details.get(self.EMAIL_KEY, ''),
            'fullname': fullname,
            'first_name': first_name,
            'last_name': last_name,
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service."""
        if self.USER_DETAILS_URL:
            return self.get_json(
                self.USER_DETAILS_URL,
                params={'access_token': access_token},
            )
        return {}

    def _get_user_name_values(self, details):
        """Return values from the given keys."""
        fullname = details.get(self.FULL_NAME_KEY, '')
        first_name = details.get(self.FIRST_NAME_KEY, '')
        last_name = details.get(self.LAST_NAME_KEY, '')
        return fullname, first_name, last_name
