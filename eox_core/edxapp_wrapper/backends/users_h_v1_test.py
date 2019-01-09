"""
Test backend to get CourseEnrollment Model.
"""

from django.db import models

def get_course_enrollment():
    """ get Test CourseEnrollment model """

    class CourseEnrollmentDummyModel(models.Model):
        pass

    return CourseEnrollmentDummyModel
