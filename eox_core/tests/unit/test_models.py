#!/usr/bin/python
"""
Test module for RedirectionModel
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from eox_core.models import Redirection


class RedirectionModelTest(TestCase):
    """
    Test the model where most of the logic is
    """

    def test_model_creation(self):
        """
        Answers the question: Can we create a model?
        """
        obj = Redirection()
        obj.domain = "localhost"
        obj.scheme = "https"
        obj.status = "302"
        obj.target = "example.com/path"

        obj.full_clean()

    def test_model_creation_fail(self):
        """
        Answers the question: If we make a wrong object, does it complain?
        """
        obj = Redirection()
        obj.domain = "localhost"
        with self.assertRaises(ValidationError):
            obj.full_clean()
