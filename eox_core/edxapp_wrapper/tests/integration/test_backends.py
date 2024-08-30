"""
This module tests the backends of the edxapp_wrapper
"""


# pylint: disable=import-outside-toplevel,unused-import
def test_current_settings_code_imports():
    """
    Running this imports means that our backends import the right signature
    """
    # isort:skip
    import eox_core.edxapp_wrapper.backends.bearer_authentication_j_v1
    import eox_core.edxapp_wrapper.backends.certificates_m_v1
    import eox_core.edxapp_wrapper.backends.comments_service_users_j_v1
    import eox_core.edxapp_wrapper.backends.configuration_helpers_h_v1
    import eox_core.edxapp_wrapper.backends.coursekey_m_v1
    import eox_core.edxapp_wrapper.backends.edxfuture_o_v1
    import eox_core.edxapp_wrapper.backends.grades_h_v1
    import eox_core.edxapp_wrapper.backends.pre_enrollment_l_v1
    import eox_core.edxapp_wrapper.backends.storages_i_v1
    import eox_core.edxapp_wrapper.backends.third_party_auth_l_v1
