"""
TODO: add me
"""
from __future__ import unicode_literals

import six
from rest_framework import relations


class CustomRelatedField(relations.RelatedField):  # pylint: disable=abstract-method
    """
    A read only field that represents its targets using the site field
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        self.field = kwargs.pop('field')
        super().__init__(**kwargs)

    def to_representation(self, value):
        return six.text_type(getattr(value, self.field))
