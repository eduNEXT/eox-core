#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for CourseKey under the open-release/hawthorn.beta1 tag
"""
from __future__ import absolute_import, unicode_literals

import mock
from django.conf import settings
from django.test import TestCase

from ..coursekey import get_valid_course_key, validate_org


class CourseKeyTest(TestCase):
    """ Tests correct load of CourseKey module """

    def setUp(self):
        """ setup """
        super(CourseKeyTest, self).setUp()
        self.m_course_id = "course-v1:org+course+run"

    @mock.patch('eox_core.edxapp_wrapper.coursekey.import_module')
    def test_import_the_backend(self, m_import):
        """ Test we import the correct backend defined in the settings """

        validate_org(self.m_course_id)
        m_import.assert_called_with(settings.EOX_CORE_COURSEKEY_BACKEND)

    @mock.patch('eox_core.edxapp_wrapper.coursekey.import_module')
    def test_call_the_backend(self, m_import):
        """ Test we use the imported backend """
        m_coursekey_backend = mock.MagicMock()
        m_import.return_value = m_coursekey_backend

        validate_org(self.m_course_id)
        m_coursekey_backend.validate_org.assert_called_with(self.m_course_id)

        get_valid_course_key(self.m_course_id)
        m_coursekey_backend.get_valid_course_key.assert_called_with(self.m_course_id)
