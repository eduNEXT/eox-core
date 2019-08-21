#!/usr/bin/python
"""
Test module for Utils
"""
from django.test import TestCase

from eox_core.utils import fasthash


class UtilsTest(TestCase):
    """
    Test the functions included on utils module
    """

    def test_fasthash_call(self):
        """
        Answers the question: Can we apply the fasthash method?
        """
        test_str = "test_str"
        fasthash(test_str)
