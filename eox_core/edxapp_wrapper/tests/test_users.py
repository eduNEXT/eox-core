""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals

import mock
from django.conf import settings
from django.test import TestCase

from ..users import create_edxapp_user


class CreateEdxappUserTest(TestCase):
    """ Tests for the public API module """

    @mock.patch('eox_core.edxapp_wrapper.users.import_module')
    def test_import_the_backend(self, m_import):
        """ Test we import the correct backend defined in the settings """

        create_edxapp_user()
        m_import.assert_called_with(settings.EOX_CORE_USERS_BACKEND)

    @mock.patch('eox_core.edxapp_wrapper.users.import_module')
    def test_call_the_backend(self, m_import):
        """ Test we use the imported backend """
        m_user_backend = mock.MagicMock()
        m_import.return_value = m_user_backend

        data = {
            "email": "something",
            "username": "something",
        }

        create_edxapp_user(data)
        m_user_backend.create_edxapp_user.assert_called_with(data)
