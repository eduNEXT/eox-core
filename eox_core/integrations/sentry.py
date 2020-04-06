"""
This file implements utils used for sentry integration.

See: https://github.com/eduNEXT/eox-core#integrations-with-third-party-services
"""
import importlib

from django.conf import settings


def load_class(full_class_string):
    """
    dynamically load a class from a string
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    return getattr(module, class_str)


def before_send(event, hint):
    """
    Workaround to prevent certain exceptions to be sent to sentry.io
    See: https://github.com/getsentry/sentry-python/issues/149#issuecomment-434448781
    """
    ignored_errors = ()
    for error in settings.EOX_CORE_SENTRY_IGNORED_ERRORS:
        try:
            error_class = load_class(error)
            ignored_errors += (error_class,)
        except Exception:  # pylint: disable=broad-except
            pass
    if 'exc_info' in hint and ignored_errors:
        _exc_type, exc_value, _tb = hint['exc_info']
        if isinstance(exc_value, ignored_errors):
            return None

    return event
