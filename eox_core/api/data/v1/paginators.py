"""
TODO: add me
"""
from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class DataApiResultsSetPagination(PageNumberPagination):
    """
    A subset of data of any queryset
    """
    page_size = settings.DATA_API_DEF_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = settings.DATA_API_MAX_PAGE_SIZE
