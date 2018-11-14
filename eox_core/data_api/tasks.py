"""
TODO: add me
"""
from celery import Task

from student.models import CourseEnrollment  # pylint: disable=import-error

from .serializers import CourseEnrollmentWithGradesSerializer


class EnrollmentsGrades(Task):
    """
    TODO: add me
    """

    def run(self, data, *args, **kwargs):  # pylint: disable=unused-argument
        """
        This task receives a list with enrollments, and returns the same
        enrollments with grades data
        """

        enrollments_ids = [el["id"] for el in data]
        enrollments_queryset = CourseEnrollment.objects.filter(id__in=enrollments_ids)

        serializer = CourseEnrollmentWithGradesSerializer(enrollments_queryset, many=True)

        return serializer.data
