"""
Util functions for reporting
"""
import six

from django.db.models import Q


def get_microsite_module():
    """
    Get the current microsite module
    """
    try:
        from eox_tenant.edxapp_wrapper import get_microsite_configuration
        return get_microsite_configuration.get_microsite()
    except ImportError:
        from microsite_configuration import microsite as microsite_module
        return microsite_module


def get_value_from_microsite_domain(domain, val_name, default=None):
    """
    Get val_name setting from the microsite that maps the given domain
    """
    if not domain:
        return None

    microsite = get_microsite_module()
    microsite.clear()
    microsite.set_by_domain(domain)

    return microsite.get_value(val_name, default)


def filter_queryset_by_microsite(queryset, domain, lookup_field, term_type):
    """
    This method filters a given queryset based on the org filters belonging
    to a microsite. The microsite is loaded from the given domain.
    Parameters:
        queryset: the queryset to filter
        domain: the doamin to load the microsite from
        lookup_field: the field used to filter based on the org
        term_type: type of coincidence with the passed lookup_field. Now
        two are supported:
            1) org_exact: exact coincidence with the field
            2) org_in_course_id: coincidence with the string ":<org>+"
    """
    org_filters = get_value_from_microsite_domain(
        domain, "course_org_filter"
    )
    if not org_filters:
        return queryset.none()

    term_types = {
        "org_exact": "{}",
        "org_in_course_id": ":{}+"
    }
    term = term_types.get(term_type, "{}")

    # Handling the case when the course_org_filter value is a string
    if isinstance(org_filters, six.string_types):
        term_search = term.format(org_filters)
        kwargs_filter = {
            lookup_field: term_search
        }
        queryset = queryset.filter(**kwargs_filter)
        return queryset

    # Handling the case when the course_org_filter value is a list
    query = Q()
    for org in org_filters:
        term_search = term.format(org)
        kwargs_filter = {
            lookup_field: term_search
        }
        query = query | Q(**kwargs_filter)

    queryset = queryset.filter(query)
    return queryset
