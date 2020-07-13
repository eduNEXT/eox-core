#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for PreEnrollments under the open-release/hawthorn.beta1 tag
"""
from __future__ import absolute_import, unicode_literals

import mock
from django.conf import settings
from django.test import TestCase

from ..pre_enrollments import create_pre_enrollment, delete_pre_enrollment, get_pre_enrollment, update_pre_enrollment


class PreEnrollmentTest(TestCase):
    """ Tests correct load of PreEnrollment module """

    def setUp(self):
        """ setup """
        super(PreEnrollmentTest, self).setUp()
        self.m_params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }

    @mock.patch('eox_core.edxapp_wrapper.pre_enrollments.import_module')
    def test_import_the_backend(self, m_import):
        """ Test we import the correct backend defined in the settings """

        create_pre_enrollment()
        m_import.assert_called_with(settings.EOX_CORE_PRE_ENROLLMENT_BACKEND)

    @mock.patch('eox_core.edxapp_wrapper.pre_enrollments.import_module')
    def test_call_the_backend(self, m_import):
        """ Test we use the imported backend """
        m_pre_enrollment_backend = mock.MagicMock()
        m_import.return_value = m_pre_enrollment_backend

        create_pre_enrollment(self.m_params)
        m_pre_enrollment_backend.create_pre_enrollment.assert_called_with(self.m_params)

        update_pre_enrollment(self.m_params)
        m_pre_enrollment_backend.update_pre_enrollment.assert_called_with(self.m_params)

        delete_pre_enrollment(self.m_params)
        m_pre_enrollment_backend.delete_pre_enrollment.assert_called_with(self.m_params)

        get_pre_enrollment(self.m_params)
        m_pre_enrollment_backend.get_pre_enrollment.assert_called_with(self.m_params)
