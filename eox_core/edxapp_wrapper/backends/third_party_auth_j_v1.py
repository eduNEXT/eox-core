"""Backend for the third party authentication exception middleware."""


def get_tpa_exception_middleware():
    """Get the ExceptionMiddleware class."""
    try:
        from third_party_auth.middleware import ExceptionMiddleware  # pylint: disable=import-outside-toplevel
    except ImportError:
        from django.utils.deprecation import \
            MiddlewareMixin as ExceptionMiddleware  # pylint: disable=import-outside-toplevel
    return ExceptionMiddleware
