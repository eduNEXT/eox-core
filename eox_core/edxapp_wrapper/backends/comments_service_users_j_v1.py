""" Module for the cs_comments_service User object."""
from openedx.core.djangoapps.django_comment_common.comment_client.user import User  # pylint: disable=import-error


def replace_username_cs_user(*args, **kwargs):
    """
    Replace user's username in cs_comments_service (forums).

    kwargs:
        user: edxapp user whose username is being replaced.
        new_username: new username.
    """
    user = kwargs.get("user")
    new_username = kwargs.get("new_username")

    cs_user = User.from_django_user(user)
    cs_user.replace_username(new_username)
