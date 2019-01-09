"""
Backend for grades.
"""

from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory  # pylint: disable=import-error


def get_course_grade_factory():
    """ get CourseGradeFactory object. """
    return CourseGradeFactory
