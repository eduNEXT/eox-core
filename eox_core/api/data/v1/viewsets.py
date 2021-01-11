"""
Controllers for the data-api. Used in the report generation process
"""
import random
from datetime import datetime

import six
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django_filters import rest_framework as filters  # pylint: disable=import-error
from edx_proctoring.models import ProctoredExamStudentAttempt  # pylint: disable=import-error
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from eox_core.edxapp_wrapper.certificates import get_generated_certificate
from eox_core.edxapp_wrapper.users import get_course_enrollment

from .filters import CourseEnrollmentFilter, GeneratedCerticatesFilter, ProctoredExamStudentAttemptFilter, UserFilter
from .paginators import DataApiResultsSetPagination
from .serializers import (
    CertificateSerializer,
    CourseEnrollmentSerializer,
    ProctoredExamStudentAttemptSerializer,
    UserSerializer,
)
from .tasks import EnrollmentsGrades


class DataApiViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    A generic viewset for all the instances of the data-api
    """
    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)

    pagination_class = DataApiResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    prefetch_fields = False
    # Microsite enforcement filter settings
    enforce_microsite_filter = False
    enforce_microsite_filter_lookup_field = "test_lookup_field"
    enforce_microsite_filter_term = "org_in_course_id"

    def get_queryset(self):
        """
        This method returns the queryset to be processed by the viewset
        """
        queryset = self.queryset
        if self.prefetch_fields:
            queryset = self.add_prefetch_fields_to_queryset(queryset, self.prefetch_fields)
        if self.enforce_microsite_filter:
            queryset = self.enforce_microsite_filter_qset(queryset)
        return queryset

    def add_prefetch_fields_to_queryset(self, queryset, fields=None):
        """
        This method adds prefetched fields to the queryset in order to
        reduce the number of hits to the database
        """
        if not fields:
            fields = []

        for val in fields:
            if val.get("type", "") == "prefetch":
                queryset = queryset.prefetch_related(val.get("name", ""))
            else:
                queryset = queryset.select_related(val.get("name", ""))

        return queryset

    def enforce_microsite_filter_qset(self, queryset):
        """
        This method enforces the filtering of the queryset based on the
        organization filters belonging to the queried site (which should map
        to a microsite).
        """
        # Check if multitenancy is enabled
        if not settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY:
            return queryset

        orgs_filter = getattr(settings, 'course_org_filter', set([]))

        queryset = self.filter_queryset_by_orgs(
            queryset,
            orgs_filter
        )
        return queryset

    def filter_queryset_by_orgs(self, queryset, org_filters):
        """
        This method filters a given queryset based on the org filters belonging
        to a microsite.
        """
        if not org_filters:
            return queryset.none()

        term_types = {
            "org_exact": "{}",
            "org_in_course_id": ":{}+"
        }
        term = term_types.get(self.enforce_microsite_filter_term, "{}")

        # Handling the case when the course_org_filter value is a string
        if isinstance(org_filters, six.string_types):
            term_search = term.format(org_filters)
            kwargs_filter = {
                self.enforce_microsite_filter_lookup_field: term_search
            }
            queryset = queryset.filter(**kwargs_filter)
            return queryset

        # Handling the case when the course_org_filter value is a list
        query = Q()
        for org in org_filters:
            term_search = term.format(org)
            kwargs_filter = {
                self.enforce_microsite_filter_lookup_field: term_search
            }
            query = query | Q(**kwargs_filter)

        queryset = queryset.filter(query)
        return queryset


class UsersViewSet(DataApiViewSet):  # pylint: disable=too-many-ancestors
    """
    A viewset for viewing users in the platform.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_class = UserFilter
    prefetch_fields = [
        {
            "name": "profile",
            "type": "select"
        },
        {
            "name": "usersignupsource_set",
            "type": "prefetch"
        }
    ]


class CourseEnrollmentViewset(DataApiViewSet):  # pylint: disable=too-many-ancestors
    """
    A viewset for viewing Course Enrollments.
    """
    serializer_class = CourseEnrollmentSerializer
    queryset = get_course_enrollment().objects.all()
    filter_class = CourseEnrollmentFilter
    # Microsite enforcement filter settings
    enforce_microsite_filter = True
    enforce_microsite_filter_lookup_field = "course__id__contains"
    enforce_microsite_filter_term = "org_in_course_id"


class CourseEnrollmentWithGradesViewset(DataApiViewSet):  # pylint: disable=too-many-ancestors
    """
    A viewset for viewing Course Enrollments with grades data.
    This view will create a celery task to fetch grades data for
    enrollments in the background, and will return the id of the
    celery task
    """
    serializer_class = CourseEnrollmentSerializer
    queryset = get_course_enrollment().objects.all()
    filter_class = CourseEnrollmentFilter
    # Microsite enforcement filter settings
    enforce_microsite_filter = True
    enforce_microsite_filter_lookup_field = "course__id__contains"
    enforce_microsite_filter_term = "org_in_course_id"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        now_date = datetime.now()
        string_now_date = now_date.strftime("%Y-%m-%d-%H-%M-%S")
        randnum = random.randint(100, 999)
        task_id = "data_api-" + string_now_date + "-" + str(randnum)

        named_args = {
            "data": serializer.data,
        }

        task = EnrollmentsGrades().apply_async(
            kwargs=named_args,
            task_id=task_id,
            routing_key=settings.GRADES_DOWNLOAD_ROUTING_KEY
        )

        url_task_status = request.build_absolute_uri(
            reverse("eox-core:eox-data-api:celery-data-api-tasks", kwargs={"task_id": task_id})
        )
        data_response = {
            "task_id": task.id,
            "task_url": url_task_status,
        }
        return Response(data_response, status=status.HTTP_202_ACCEPTED)


class CertificateViewSet(DataApiViewSet):  # pylint: disable=too-many-ancestors
    """
    A viewset for viewing certificates generated for users.
    """
    serializer_class = CertificateSerializer
    filter_class = GeneratedCerticatesFilter
    prefetch_fields = [
        {
            "name": "user",
            "type": "select"
        }
    ]
    # Microsite enforcement filter settings
    enforce_microsite_filter = True
    enforce_microsite_filter_lookup_field = "course_id__contains"
    enforce_microsite_filter_term = "org_in_course_id"

    def get_queryset(self):
        self.queryset = get_generated_certificate().objects.all()
        return super(CertificateViewSet, self).get_queryset()


class ProctoredExamStudentViewSet(DataApiViewSet):  # pylint: disable=too-many-ancestors
    """
    A viewset for viewing proctored exams attempts made by students.
    """

    serializer_class = ProctoredExamStudentAttemptSerializer
    queryset = ProctoredExamStudentAttempt.objects.all()
    filter_class = ProctoredExamStudentAttemptFilter
    prefetch_fields = [
        {
            "name": "user",
            "type": "select"
        },
        {
            "name": "proctored_exam",
            "type": "select"
        }
    ]
    # Microsite enforcement filter settings
    enforce_microsite_filter = True
    enforce_microsite_filter_lookup_field = "proctored_exam__course_id__contains"
    enforce_microsite_filter_term = "org_in_course_id"
