"""
TODO: add me
"""
import django_filters  # pylint: disable=import-error
from django.contrib.auth.models import User
from edx_proctoring.models import ProctoredExamStudentAttempt  # pylint: disable=import-error
from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-error

from eox_core.edxapp_wrapper.certificates import get_generated_certificate
from eox_core.edxapp_wrapper.users import get_course_enrollment


class BaseDataApiFilter(django_filters.rest_framework.FilterSet):
    """
    TODO: add me
    """
    ordering = django_filters.OrderingFilter()


class UserFilter(BaseDataApiFilter):
    """
    TODO: add me
    """
    # Filtering by main model fields
    username = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    date_joined = django_filters.DateTimeFromToRangeFilter()

    # Filtering by user profile fields
    name = django_filters.CharFilter(field_name="profile__name", lookup_expr="icontains")
    language = django_filters.CharFilter(field_name="profile__language", lookup_expr="iexact")
    year_of_birth = django_filters.RangeFilter(field_name="profile__year_of_birth")
    gender = django_filters.CharFilter(field_name="profile__gender", lookup_expr="iexact")
    mailing_address = django_filters.CharFilter(field_name="profile__mailing_address", lookup_expr="iexact")
    city = django_filters.CharFilter(field_name="profile__city", lookup_expr="icontains")
    country = django_filters.CharFilter(field_name="profile__country", lookup_expr="icontains")

    # Filtering by user signup source fields
    site = django_filters.CharFilter(field_name="usersignupsource__site", lookup_expr='iexact')

    class Meta:
        """
        TODO: add me
        """
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'date_joined',
            'name',
            'language',
            'year_of_birth',
            'gender',
            'mailing_address',
            'city',
            'country',
            'site',
        ]


class CourseEnrollmentFilter(BaseDataApiFilter):
    """
    TODO: add me
    """
    course_id = django_filters.CharFilter(method="filter_course_id")
    created = django_filters.DateTimeFromToRangeFilter()
    is_active = django_filters.BooleanFilter()
    mode = django_filters.CharFilter(lookup_expr='icontains')
    site = django_filters.CharFilter(field_name="user__usersignupsource__site", lookup_expr='iexact')

    def filter_course_id(self, queryset, name, value):
        """
        This custom filter was created to enable filtering by course_id.
        See common.djangoapps.xmodule_django.models
        When doing queries over opaque fields, we need to instance the
        KEY_CLASS of the field with the query string first, and then pass
        this instance to the queryset filter.
        In this case, the KEY_CLASS for course_id field is CourseKey
        """
        if value:
            # CourseKey instance creation will fail if course does not exist
            try:
                # Instantiating CourseKey of the field with query string
                instance = CourseKey.from_string(str(value))
                # Passing instance to queryset filter
                return queryset.filter(course_id=instance)
            except Exception:  # pylint: disable=broad-except
                # If CourseKey instantiation fails, return an empty queryset
                return queryset.none()

        return queryset

    class Meta:
        """
        TODO: add me
        """
        model = get_course_enrollment()
        fields = [
            'id',
            'course_id',
            'created',
            'is_active',
            'mode',
            'site',
        ]


class GeneratedCerticatesFilter(BaseDataApiFilter):
    """
    TODO: add me
    """
    DOWNLOADABLE = 'downloadable'
    ALL = 'all'

    site = django_filters.CharFilter(field_name="user__usersignupsource__site", lookup_expr='iexact')
    username = django_filters.CharFilter(field_name="user__username", lookup_expr='icontains')
    created_date = django_filters.DateTimeFromToRangeFilter()
    course_id = django_filters.CharFilter(method="filter_course_id")
    status = django_filters.CharFilter(method="filter_status")
    grade = django_filters.CharFilter()
    mode = django_filters.CharFilter()

    def filter_course_id(self, queryset, name, value):
        """
        This custom filter was created to enable filtering by course_id.
        See common.djangoapps.xmodule_django.models
        When doing queries over opaque fields, we need to instance the
        KEY_CLASS of the field with the query string first, and then pass
        this instance to the queryset filter.
        In this case, the KEY_CLASS for course_id field is CourseKey
        """
        if value:
            # CourseKey instance creation will fail if course does not exist
            try:
                # Instantiating CourseKey of the field with query string
                instance = CourseKey.from_string(str(value))
                # Passing instance to queryset filter
                return queryset.filter(course_id=instance)
            except Exception:  # pylint: disable=broad-except
                # If CourseKey instantiation fails, return an empty queryset
                return queryset.none()

        return queryset

    def filter_status(self, queryset, name, value):
        """
        This custom filter was created to return a queryset
        where certificates have downloadable status or
        another queryset with all available certificates.
        """
        if value:
            if value == self.DOWNLOADABLE:
                return queryset.filter(status=value)
            if value == self.ALL:
                return queryset.exclude(status=self.DOWNLOADABLE)

        return queryset

    class Meta:
        """
        TODO: add me
        """
        model = get_generated_certificate()
        fields = [
            'id',
            'course_id',
            'grade',
            'mode',
            'username',
            'status',
            'site',
            'created_date'
        ]


class ProctoredExamStudentAttemptFilter(BaseDataApiFilter):
    """
    TODO: add me
    """
    site = django_filters.CharFilter(field_name="user__usersignupsource__site", lookup_expr='iexact')
    course_id = django_filters.CharFilter(field_name="proctored_exam__course_id", lookup_expr='iexact')
    exam_name = django_filters.CharFilter(field_name="proctored_exam__exam_name", lookup_expr='iexact')

    class Meta:
        """
        TODO: add me
        """
        model = ProctoredExamStudentAttempt
        fields = [
            'id',
            'site',
            'course_id',
            'exam_name'

        ]
