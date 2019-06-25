"""
Util functions for reporting
"""
import copy

from django.db.models import Q


def get_microsite_backend():
    """
    Get the current microsite backend
    """
    try:
        from eox_tenant.edxapp_wrapper import get_microsite_configuration
        return get_microsite_configuration.get_microsite().BACKEND
    except ImportError:
        from microsite_configuration import microsite
        return microsite.BACKEND


def get_microsite_config_by_domain(domain):
    """
    Get microsite config from a given domain
    """
    values = {}
    backend = get_microsite_backend()
    # If the backend support the get_config_by_domain method, just use it
    if getattr(backend, "get_config_by_domain"):
        values, __ = backend.get_config_by_domain(domain)
        return values

    # Handle classic backends
    # Save old microsite backend config
    old_config = copy.deepcopy(backend.current_request_configuration.data)
    # Set config in microsite backend according to the passed domain
    backend.set_config_by_domain(domain)
    if backend.current_request_configuration.data.get('site_domain') == domain:
        values = copy.deepcopy(backend.current_request_configuration.data)

    backend.current_request_configuration.data = old_config
    return values


def get_org_filters_from_microsite(domain):
    """
    Get course_org_filter setting from microsite having the given domain
    """
    if not domain:
        return None

    config_by_domain = get_microsite_config_by_domain(domain)
    if not config_by_domain:
        return None

    org_filters = config_by_domain.get("course_org_filter", [])
    return org_filters


def filter_queryset_by_microsite(queryset, domain, lookup, term_type):
    """
    TODO: add me
    """
    org_filters = get_org_filters_from_microsite(domain)
    if not org_filters:
        return queryset.none()

    term_types = {
        "org_exact": "{}",
        "org_in_course_id": ":{}+"
    }
    term = term_types.get(term_type, "{}")

    # Handling the case when the course_org_filter value is a string
    if isinstance(org_filters, (unicode, str)):
        term_search = term.format(org_filters)
        kwargs_filter = {
            lookup: term_search
        }
        queryset = queryset.filter(**kwargs_filter)
        return queryset

    # Handling the case when the course_org_filter value is a list
    query = Q()
    for org in org_filters:
        term_search = term.format(org)
        kwargs_filter = {
            lookup: term_search
        }
        query = query | Q(**kwargs_filter)

    queryset = queryset.filter(query)
    return queryset
