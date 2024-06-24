"""
Test integration file.
"""
from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=['testserver'], SITE_ID=2)
class TutorIntegrationTestCase(TestCase):
    """
    Tests integration with openedx
    """

    def setUp(self):
        """
        Set up the base URL for the tests
        """
        self.base_url = 'http://local.edly.io'

    # pylint: disable=import-outside-toplevel,unused-import
    def test_current_settings_code_imports(self):
        """
        Running this imports means that our backends import the right signature
        """
        import eox_core.edxapp_wrapper.backends.bearer_authentication_j_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.certificates_m_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.comments_service_users_j_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.configuration_helpers_h_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.coursekey_m_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.edxfuture_o_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.grades_h_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.storages_i_v1  # isort:skip
        import eox_core.edxapp_wrapper.backends.third_party_auth_l_v1  # isort:skip

    def test_info_view(self):
        """
        Tests the info view endpoint in Tutor
        """
        info_view_url = f'{self.base_url}/eox-core/eox-info'

        response = self.client.get(info_view_url)

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIn('version', response_data)
        self.assertIn('name', response_data)
        self.assertIn('git', response_data)
