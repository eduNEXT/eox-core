"""
The pipeline module defines functions that are used in the third party authentication flow
"""
import logging
from eox_core.edxapp_wrapper.users import get_user_profile

LOG = logging.getLogger(__name__)


# pylint: disable=unused-argument,keyword-arg-before-vararg
def ensure_user_has_profile(backend, details, user=None, *args, **kwargs):
    """
    This pipeline function creates an empty profile object if the user does not have one.
    It can be used with the user_details_force_sync function to fill the profile after creation.
    """
    if user:
        user_profile_model = get_user_profile()
        try:
            __ = user.profile
        except user_profile_model.DoesNotExist:
            user_profile_model.objects.create(user=user)
            LOG.info('Created new profile for user during the third party pipeline: "%s"', user)
