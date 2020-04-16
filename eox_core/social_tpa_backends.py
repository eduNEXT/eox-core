"""
Extensions to the regular defined third party auth backends
"""
import logging

from django.conf import settings
from social_core.backends.open_id_connect import OpenIdConnectAuth

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
            except Exception as e:
                LOG.error("Tried and failed to set property %s of a config-based-openidconnect", key)

        super(ConfigurableOpenIdConnectAuth, self).__init__(*args, **kwargs)
