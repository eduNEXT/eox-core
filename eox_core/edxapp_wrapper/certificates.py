"""
Certificates definitions.
"""

from importlib import import_module

from django.conf import settings


def get_generated_certificate():
    """ Gets GeneratedCertificate model. """

    backend_function = settings.EOX_CORE_CERTIFICATES_BACKEND
    backend = import_module(backend_function)

    return backend.get_generated_certificate()
