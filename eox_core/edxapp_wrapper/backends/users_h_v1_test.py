"""
Test backend to get CourseEnrollment Model.
"""

from django.contrib.auth.models import Permission


def get_course_enrollment():
    """
    Get Test CourseEnrollment model.

    We return any django model that already exists so that
    django-filters is happy and no migrations are created.
    """
    return Permission
