"""
LanguagePreferenceMiddleware Backend.
"""


def get_language_preference_middleware():
    """Backend to get the LanguagePreferenceMiddleware from openedx."""
    class LanguagePreferenceMiddleware:
        """LanguagePreferenceMiddleware Backend Mock."""
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            # Simulate the behavior of LanguagePreferenceMiddleware
            # For example, set a language preference in the request
            request.LANGUAGE_CODE = 'en'
            return self.get_response(request)
    return LanguagePreferenceMiddleware
