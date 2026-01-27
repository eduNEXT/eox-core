"""
Celery tasks for eox_core.
"""
import logging

from celery import shared_task

retirement_logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def delete_user_task(self, user_id, username):
    """
    Celery task to delete a user after a short delay.

    This task is executed asynchronously to give the retirement pipeline sender
    time to finish updating and saving the user before the actual deletion.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        retirement_logger.info("User deleted successfully: %s", username)
    except User.DoesNotExist:
        retirement_logger.warning(
            "User %s (id=%s) already deleted or does not exist",
            username,
            user_id,
        )
    except Exception as e:  # pylint: disable=broad-except
        retirement_logger.error("Failed to delete user %s: %s", username, e, exc_info=True)
        raise self.retry(exc=e)
