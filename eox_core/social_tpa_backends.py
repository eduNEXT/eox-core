"""
Extensions to the regular defined third party auth backends
"""
import logging

from django.conf import settings

from eox_core.edxapp_wrapper.configuration_helpers import get_configuration_helper

try:
    from social_core.backends.open_id_connect import OpenIdConnectAuth
except ImportError:
    OpenIdConnectAuth = object
try:
    from social_core.exceptions import AuthMissingParameter
except ImportError:
    AuthMissingParameter = Exception

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

    def oidc_config(self):
        """
        Override method that gets OICD configuration per class instance.
        """
        LOG.debug(
            "Be aware that ConfigurableOpenIdConnectAuth is using an override "
            "method to get OICD configuration."
        )
        if not hasattr(self, 'configuration'):
            self.configuration = self.get_json(  # pylint: disable=attribute-defined-outside-init
                self.OIDC_ENDPOINT + '/.well-known/openid-configuration'
            )
        return self.configuration

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
        """
        Get information returned by the provider including user information.

        When debug mode is enabled, the entire response from the provided is
        added. This behavior is controlled via site settings:

        - 'SOCIAL_AUTH_DEBUG_ENABLED': if true, then debug mode is enabled.
        default is set to false.

        Examples:
            - Default mode
            {
                'refresh_token': None,
                ...
                'user_details':
                {
                    'first_name': 'Test',
                    'last_name': 'Subject',
                    ...
                },
                ...
            }
            - Debug mode enabled -after enabled once- or exception raised
            {
                ...
                'user_details': ...,
                'userinfo_response':
                {
                    'locale': 'es',
                    'hd': 'edunext.co',
                    'given_name': 'Test',
                    'email': 'test.subject@edunext.co',
                    'family_name': 'Subject',
                    ...
                    'email_verified': True,
                    'expires_in': 3598,
                    'picture': ...,
            }
        """
        data = super().extra_data(user, uid, response, details, *args, **kwargs)

        debug_mode_enabled = self.setting('DEBUG_ENABLED', False)

        try:
            data["user_details"] = self.get_user_details(response)
            if debug_mode_enabled:
                data["userinfo_response"] = response
        except Exception:  # pylint: disable=broad-except
            LOG.exception("An exception was raised while loading user_details.")
            data["userinfo_response"] = response

        return data

    def get_user_id(self, *args, **kwargs):
        """
        Insert a slug at the beginning of the user id. Retroactively add the
        slug for social users that don't have one. The slug must be defined
        in the 'OTHER_SETTINGS' field from the provider configuration.
        In case a slug was not defined raise an exception due to misconfigured
        backend.
        This three behaviours can be controlled via the settings:
            - 'SOCIAL_AUTH_NAMESPACED_UIDS': if false behave as originally
            intended. If true, add a slug to the uid.
            - 'SOCIAL_AUTH_ALLOW_SLUGLESS_UID': if false raise and exception when no slug
            is defined. If true, return de original uid when no slug is defined.
            - 'SOCIAL_AUTH_ALLOW_WRITE_SLUG_UID': If true update the uid of existing social
            users if any.

        A first step to start migrating to name spaced uids would look like this:

        on the site settings:
        {
          "SOCIAL_AUTH_NAMESPACED_UIDS": true,
          "SOCIAL_AUTH_ALLOW_SLUGLESS_UID": true,
          "SOCIAL_AUTH_ALLOW_WRITE_SLUG_UID": true
        }

        on the provider configuration:
            OTHER_SETTINGS:
            {
              "slug": "myslug"
            }

        Setting 'SOCIAL_AUTH_NAMESPACED_UIDS' to true and adding the slug to
        'OTHER_SETTINGS' will create new associations with the new format.
        'SOCIAL_AUTH_ALLOW_WRITE_SLUG_UID'=true  will update older entries to the new
        format at login time and 'SOCIAL_AUTH_ALLOW_SLUGLESS_UID'=true would allow
        the previous format for older entries for the time being.

        Once all the old uids have been updated to the new format we can forbid the
        old format altogether and stop trying to updated uids without a slug.

        on the site settings:
        {
          "SOCIAL_AUTH_NAMESPACED_UIDS": true,
          "SOCIAL_AUTH_ALLOW_SLUGLESS_UID": false,
          "SOCIAL_AUTH_ALLOW_WRITE_SLUG_UID": false
        }

        on the provider configuration:
            OTHER_SETTINGS:
            {
              "slug": "myslug"
            }
        """
        uid = super().get_user_id(*args, **kwargs)
        namespaced_uids = self.setting('NAMESPACED_UIDS', False)
        if not namespaced_uids:
            return uid

        strategy = self.strategy
        slug = strategy.setting('slug', backend=self)
        provider = self.name
        allow_slugless_uid = self.setting('ALLOW_SLUGLESS_UID', False)
        allow_write_slug_uid = self.setting('ALLOW_WRITE_SLUG_UID', True)

        if not slug:
            if allow_slugless_uid:
                return uid
            raise AuthMissingParameter(self, 'slug')

        slug_uid = '{0}:{1}'.format(slug, uid)
        if allow_write_slug_uid:
            social = strategy.storage.user.get_social_auth(provider, uid)
            if social:
                social.uid = slug_uid
                social.save()
                LOG.info("Updating uid: %s to %s", uid, slug_uid)

        return slug_uid
