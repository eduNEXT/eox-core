"""
Backend for certificates app.
"""

from lms.djangoapps.certificates.api import get_certificate_url as _get_certificate_url  # pylint: disable=import-error
from lms.djangoapps.certificates.models import GeneratedCertificate  # pylint: disable=import-error
from lms.djangoapps.certificates.tasks import generate_certificate  # pylint: disable=import-error


def get_generated_certificate():
    """Get GeneratedCertificate model."""
    return GeneratedCertificate


def get_generate_certificate_task(**kwargs):
    """Get generate_certificate_task task."""
    return generate_certificate(**kwargs)


def get_certificate_url(**kwargs):
    """Get get_certificate_url function."""
    return _get_certificate_url(**kwargs)
