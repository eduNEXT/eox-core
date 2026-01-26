"""
Signal handlers for platform_plugins_ca.

This module handles:
1. Account deactivation logging (when user requests deletion via deactivate_logout)
2. User retirement signal handling (MetaRed policy: permanent deletion after pipeline)

The retirement handlers listen for USER_RETIRE_LMS_CRITICAL signal at the END
of the retirement pipeline to permanently delete users, allowing email reuse.
"""
import logging

from django.contrib.auth.signals import user_logged_out
from django.db import transaction
from django.dispatch import Signal, receiver
from openedx.core.djangoapps.user_api.accounts.signals import (  # pylint: disable=import-error
    USER_RETIRE_LMS_CRITICAL,
    USER_RETIRE_LMS_MISC,
)
from openedx.core.djangoapps.user_api.models import UserRetirementStatus  # pylint: disable=import-error

try:
    from common.djangoapps.student.models import UserProfile
    from common.djangoapps.util.model_utils import USER_FIELDS_CHANGED
    from lms.djangoapps.certificates.api import get_recently_modified_certificates
except ImportError:
    UserProfile = None
    USER_FIELDS_CHANGED = Signal()
    get_recently_modified_certificates = None

logger = logging.getLogger("platform_plugins_ca.deactivation")
retirement_logger = logging.getLogger("platform_plugins_ca.retirement")


@receiver(user_logged_out)
def handle_account_deactivation(sender, request, user, **kwargs):
    """
    Signal receiver for user logout events.

    Logs when a user requests account deletion via the deactivate_logout endpoint.
    The actual deletion happens later via the retirement pipeline.
    """
    if not user:
        return

    if request and 'deactivate_logout' in request.path:
        logger.info(
            "ACCOUNT_DEACTIVATION_INITIATED: User requested account deletion. "
            "user_id=%s, username=%s, email=%s. "
            "User will be deleted after retirement pipeline completes.",
            user.id,
            user.username,
            user.email,
        )


@receiver(USER_RETIRE_LMS_MISC)
def handle_retire_lms_misc(sender, user, **kwargs):
    """
    Signal receiver for USER_RETIRE_LMS_MISC retirement step.

    Logs when the LMS_MISC retirement step is reached for a user.
    """
    retirement_logger.info(
        "[METARED_RETIREMENT] USER_RETIRE_LMS_MISC signal received - "
        "sender=%s, user=%s, kwargs=%s",
        sender,
        user,
        kwargs,
    )

    if not user:
        retirement_logger.warning(
            "[METARED_RETIREMENT] LMS_MISC step received with None user - ignoring"
        )
        return

    try:
        user_id = getattr(user, 'id', None)
        username = getattr(user, 'username', None)
        email = getattr(user, 'email', None)
        retirement_logger.info(
            "[METARED_RETIREMENT] LMS_MISC step for user: %s (id=%s, email=%s)",
            username,
            user_id,
            email,
        )
    except Exception as e:  # pylint: disable=broad-except
        retirement_logger.error(
            "[METARED_RETIREMENT] Error accessing user attributes in LMS_MISC: %s",
            e,
            exc_info=True,
        )


@receiver(USER_RETIRE_LMS_CRITICAL)
def handle_retire_lms_critical(sender, user, **kwargs):
    """
    Signal receiver for USER_RETIRE_LMS_CRITICAL retirement step.

    Permanently deletes the user after the retirement pipeline completes.
    This implements the MetaRed policy allowing email reuse after deletion.
    """
    retirement_logger.info(
        "[METARED_RETIREMENT] USER_RETIRE_LMS_CRITICAL signal received - "
        "sender=%s, user=%s, kwargs=%s",
        sender,
        user,
        kwargs,
    )

    if not user:
        retirement_logger.warning(
            "[METARED_RETIREMENT] LMS_CRITICAL step received with None user - ignoring"
        )
        return

    try:
        user_id = getattr(user, 'id', None)
        username = getattr(user, 'username', None)
        email = getattr(user, 'email', None)
        retirement_logger.info(
            "[METARED_RETIREMENT] LMS_CRITICAL step for user: %s (id=%s, email=%s) - deleting now",
            username,
            user_id,
            email,
        )
    except Exception as e:  # pylint: disable=broad-except
        retirement_logger.error(
            "[METARED_RETIREMENT] Error accessing user attributes in LMS_CRITICAL: %s",
            e,
            exc_info=True,
        )
        return

    delete_user_permanently(user)


def delete_user_permanently(user):
    """
    Permanently delete a user from the database.

    This function deletes the UserRetirementStatus record first (since it
    references the user), then deletes the user record itself. This allows
    the user to re-register with the same email address (MetaRed policy).

    Parameters
    ----------
    user : User
        The Django user instance to delete.
    """
    if not user:
        retirement_logger.warning(
            "[METARED_RETIREMENT] delete_user_permanently called with None user - ignoring"
        )
        return

    try:
        user_id, username, email = user.id, user.username, user.email
    except AttributeError as e:
        retirement_logger.error(
            "[METARED_RETIREMENT] User object missing required attributes: %s",
            e,
        )
        return

    retirement_logger.info(
        "[METARED_RETIREMENT] Deleting user: %s (id=%s, email=%s)",
        username,
        user_id,
        email,
    )

    try:
        with transaction.atomic():
            UserRetirementStatus.objects.filter(user=user).delete()
            user.delete()
            retirement_logger.info(
                "[METARED_RETIREMENT] User deleted: %s - can re-register with %s",
                username,
                email,
            )

    except Exception as e:  # pylint: disable=broad-except
        retirement_logger.error(
            "[METARED_RETIREMENT] Failed to delete user %s: %s",
            username,
            e,
            exc_info=True,
        )


def connect_signals():
    """
    Connect all signal receivers for platform_plugins_ca.

    This function is called from the AppConfig.ready() method to ensure
    signals are registered when Django starts.

    Note: The @receiver decorators handle signal connection automatically,
    but this function provides a hook for logging and any future manual
    signal connections.
    """
    logger.info(
        "SIGNALS: platform_plugins_ca signal receivers configured "
        "(deactivation logging + retirement handlers)"
    )
    retirement_logger.info(
        "[METARED_RETIREMENT] Signal handlers registered: "
        "USER_RETIRE_LMS_MISC -> handle_retire_lms_misc, "
        "USER_RETIRE_LMS_CRITICAL -> handle_retire_lms_critical"
    )


# pylint: disable=unused-argument
@receiver(USER_FIELDS_CHANGED)
def update_certificates_for_user(sender, user, table, changed_fields, **kwargs):
    """
    Update certificates when a user's name changes.

    This handler listens to the `USER_FIELDS_CHANGED` signal and updates the name of
    the certificates of the user if the user's name has changed.

    Args:
        sender: The model class that sent the signal.
        user: The User instance whose fields have changed.
        table: The database table name where the change occurred.
        changed_fields: Dictionary mapping field names to (old_value, new_value) tuples.
        **kwargs: Additional keyword arguments passed by the signal.
    """
    # Only update certificates if the user's name has changed
    if table == UserProfile._meta.db_table and "name" in changed_fields:
        certificates = get_recently_modified_certificates(user_ids=[user.id])
        certificates.update(name=user.profile.name)
