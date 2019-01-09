"""
Backend for certificates app.
"""

from lms.djangoapps.certificates.models import GeneratedCertificate  # pylint: disable=import-error


def get_generated_certificate():
    """ get GeneratedCertificate model. """
    return GeneratedCertificate
