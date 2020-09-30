"""
Test backend to get CourseEnrollment Model.
"""

from django.contrib.auth.models import Permission

USERNAME_MAX_LENGTH = 30


def get_edxapp_user(**kwargs):
    """
    Return a fake user
    """
    return object


def create_edxapp_user(*args, **kwargs):
    """
    Return a fake user and a list of errors
    """
    return object, []


def get_user_read_only_serializer():
    """
    Return a fake user read only serializer
    """
    try:
        from openedx.core.djangoapps.user_api.accounts.serializers import UserReadOnlySerializer
    except ImportError:
        UserReadOnlySerializer = object
    return UserReadOnlySerializer


def check_edxapp_account_conflicts(email, username):
    """
    Get an executes the check_account_exists for tests
    """
    try:
        from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
    except ImportError:
        def check_account_exists(email=None, username=None):
            """
            Fake definition for check_account_exists edxapp function
            """
            return email and username
    return check_account_exists(email=email, username=username)


def get_course_enrollment():
    """
    Get Test CourseEnrollment model.

    We return any django model that already exists so that
    django-filters is happy and no migrations are created.
    """
    return Permission


def get_course_team_user(*args, **kwargs):
    """
    Return a fake course team user
    """
    return object


def get_user_signup_source():
    """
    Get test UserSignupSource model
    """
    try:
        from student.models import UserSignupSource
    except ImportError:
        UserSignupSource = object
    return UserSignupSource


def get_user_profile():
    """ Gets the UserProfile model """
    try:
        from student.models import UserProfile
    except ImportError:
        UserProfile = object
    return UserProfile
