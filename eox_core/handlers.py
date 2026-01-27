"""
Signal handlers for eox_core.

This module handles user retirement signal handling (MetaRed policy: permanent deletion
after pipeline completion to allow email reuse).

The deletion is executed via a background task with a short delay to avoid conflicts
with the sender still modifying and saving the user instance after the signal is emitted.
"""
import logging

from django.dispatch import receiver

from openedx.core.djangoapps.user_api.accounts.signals import USER_RETIRE_LMS_MISC  # pylint: disable=import-error

from eox_core.tasks import delete_user_task

retirement_logger = logging.getLogger(__name__)

DEFAULT_LMS_QUEUE = "edx.lms.core.default"


@receiver(USER_RETIRE_LMS_MISC)
def handle_retire_user(sender, user, **kwargs):  # pylint: disable=unused-argument
    """
    Signal receiver for USER_RETIRE_LMS_MISC retirement step.

    Schedules the permanent deletion of the user via a background task with a short
    delay. This implements the MetaRed policy allowing email reuse after deletion.
    """
    if not user:
        retirement_logger.warning("Retirement signal received with None user - ignoring")
        return

    username = user.username
    user_id = user.id

    retirement_logger.info("Scheduling deletion for user: %s (id=%s)", username, user_id)

    # Schedule deletion with a 10-second delay to let the pipeline finish.
    delete_user_task.apply_async(
        args=[user_id, username],
        countdown=10,
        queue=DEFAULT_LMS_QUEUE,
        routing_key=DEFAULT_LMS_QUEUE,
    )
