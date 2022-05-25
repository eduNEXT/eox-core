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


def generate_certificate_task(**kwargs):
    """Get generate_certificate_task task."""
    backend_function = settings.EOX_CORE_CERTIFICATES_BACKEND
    backend = import_module(backend_function)

    return backend.get_generate_certificate_task(**kwargs)


def get_certificate_url(**kwargs):
    """Get certificate URL function."""
    backend_function = settings.EOX_CORE_CERTIFICATES_BACKEND
    backend = import_module(backend_function)

    return backend.get_certificate_url(**kwargs)
