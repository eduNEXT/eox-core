"""
Routers for the API views.
"""

from rest_framework import routers

from .viewsets import (
    CertificateViewSet,
    CourseEnrollmentViewset,
    CourseEnrollmentWithGradesViewset,
    ProctoredExamStudentViewSet,
    UsersViewSet,
)

ROUTER = routers.DefaultRouter()
ROUTER.register(r"users", UsersViewSet, basename="users")
ROUTER.register(r"course-enrollments", CourseEnrollmentViewset, basename="course-enrollments")
ROUTER.register(r"certificates", CertificateViewSet, basename="generated_certificate")
ROUTER.register(r"proctored-exams-attempts", ProctoredExamStudentViewSet, basename="proctored_exams_attempts")
# Async operations
ROUTER.register(
    r"async/course-enrollments-grades", CourseEnrollmentWithGradesViewset, basename="async_course-enrollments-grades"
)
