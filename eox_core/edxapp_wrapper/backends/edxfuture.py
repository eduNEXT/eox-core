"""
Functions copied from a version higer than hawtorn (for backwards compatibility with i)
Must be deleted some day and replaced with calls to the actual functions
"""
from django.core.cache import cache
from django.conf import settings
from edx_rest_api_client.client import EdxRestApiClient


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

    program = EdxRestApiClient(self.catalog_api_url, jwt=self.access_token).programs(program_uuid).get()
    cache.set(cache_key, program, settings.PROGRAMS_CACHE_TTL)

    return program
