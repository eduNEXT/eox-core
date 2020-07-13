"""
Functions copied from a version higer than hawthorn (for backwards compatibility with it)
Must be deleted some day and replaced with calls to the actual functions
"""
from django.conf import settings
# pylint: disable=import-error
from django.core.cache import cache
from openedx.core.djangoapps.catalog.models import CatalogIntegration
from openedx.core.djangoapps.catalog.utils import create_catalog_api_client


def get_program(program_uuid, ignore_cache=False):
    """
    Retrieves the details for the specified program.

     Args:
         program_uuid (UUID): Program identifier
         ignore_cache (bool): Indicates if previously-cached data should be ignored.

     Returns:
         dict
    """
    program_uuid = str(program_uuid)
    cache_key = 'programs.api.data.{uuid}'.format(uuid=program_uuid)

    if not ignore_cache:
        program = cache.get(cache_key)

        if program:
            return program

    catalog_integration = CatalogIntegration.current()
    user = catalog_integration.get_service_user()
    api = create_catalog_api_client(user)

    program = api.programs(program_uuid).get()
    cache.set(cache_key, program, getattr(settings, 'PROGRAMS_CACHE_TTL', 60))

    return program
