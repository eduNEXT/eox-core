#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for CourseKey validations under the open-release/hawthorn.beta1 tag
"""
from django.test import TestCase
from mock import patch
from rest_framework.serializers import ValidationError

from ..serializers import EdxappCourseEnrollmentSerializer


class CourseKeyValidationTest(TestCase):
    """ Tests for the CourseKey validations """

    def setUp(self):
        """ setup """
        super(CourseKeyValidationTest, self).setUp()
        self.enrollment_serializer = EdxappCourseEnrollmentSerializer
        self.m_enrollment = {
            'mode': 'audit',
            'user': 'test',
            'is_active': True,
        }

    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.check_edxapp_enrollment_is_valid', return_value=[])
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    def test_incorrect_course_id(self, m_get_valid_course_key, *_):
        """ Test that the CourseKey validation fails due to invalid formatting """
        course_id = "test1234"
        m_get_valid_course_key.side_effect = ValidationError("Invalid course_id {}".format(course_id))
        self.m_enrollment['course_id'] = course_id
        serializer = self.enrollment_serializer(data=self.m_enrollment)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        m_get_valid_course_key.assert_called_once_with(course_id)

    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.serializers.check_edxapp_enrollment_is_valid', return_value=[])
    def test_course_id_valid_org(self, _, m_get_valid_course_key, m_validate_org):
        """ Test that the CourseKey validation fails because it doesn't belong to the filtered org """
        course_id = "course-v1:org+course+run"
        m_get_valid_course_key.return_value = None
        m_validate_org.return_value = False

        self.m_enrollment['course_id'] = course_id
        serializer = self.enrollment_serializer(data=self.m_enrollment)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        m_validate_org.assert_called_once_with(course_id)

    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.serializers.check_edxapp_enrollment_is_valid', return_value=[])
    def test_course_id_correct(self, _, m_get_valid_course_key, m_validate_org):
        """ Test that the CourseKey validation works under normal conditions """
        course_id = "course-v1:org+course+run"
        m_get_valid_course_key.return_value = None
        m_validate_org.return_value = True

        self.m_enrollment['course_id'] = course_id
        serializer = self.enrollment_serializer(data=self.m_enrollment)

        serializer.is_valid(raise_exception=True)

        m_validate_org.assert_called_once_with(course_id)
        m_get_valid_course_key.assert_called_once_with(course_id)
