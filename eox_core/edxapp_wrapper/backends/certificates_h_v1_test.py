"""
Test backend to get GenerateCertificates Model.
"""

from django.contrib.auth.models import Permission


def get_generated_certificate():
    """
    Get test GeneratedCertificate model.

    We return any django model that already exists so that
    django-filters is happy and no migrations are created.
    """
    return Permission
