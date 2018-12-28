"""
Test backend to get GenerateCertificates Model.
"""

from django.db import models

def get_generated_certificate():
    """ get test GeneratedCertificate model. """

    class CertificatesDummyModel(models.Model):
        pass

    return CertificatesDummyModel
