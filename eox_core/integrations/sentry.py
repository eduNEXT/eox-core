"""
This file implements utils used for sentry integration.

See: https://github.com/eduNEXT/eox-core#integrations-with-third-party-services
"""
import re
import importlib
import six

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


class ExceptionFilterSentry(object):
    """
    This class is a helper to filter exception events before send them to
    sentry.io service (See: https://github.com/getsentry/sentry-python/issues/149#issuecomment-434448781).
    It relies on the EOX_CORE_SENTRY_IGNORED_ERRORS setting. This setting is a list of rules that defines
    which exceptions to ignore. An example below:

    EOX_CORE_SENTRY_IGNORED_ERRORS = [
        {
            "exc_class": "openedx.core.djangoapps.user_authn.exceptions.AuthFailedError",
            "exc_text": ["AuthFailedError.*Email or password is incorrect"]
        },
    ]
    Every rule support only 2 keys for now:
    - exc_class: the path to the exception class we want to ignore. It can only be one
    - exc_text: a list of regex expressions to search on the last traceback frame text of the exception

    In this example we have only one rule. We are ignoring AuthFailedError exceptions whose traceback text
    has a match with the regex provided in the exc_text unique element. If exc_text contains more than one
    regex, the exception is ignored if any of the regex matches the traceback text.
    """
    hint = None
    exc_text = ''
    exc_value = None

    validation_exc_methods = {
        'exc_class': 'validate_exc_class',
        'exc_text': 'validate_exc_text'
    }

    def init_exception_values(self, event, hint):
        """
        Initialization of required values
        """
        self.hint = hint

        if 'log_record' in hint:
            self.exc_text = getattr(hint['log_record'], 'exc_text', '')

        if 'exc_info' in hint:
            _exc_type, exc_value, _tb = hint['exc_info']
            self.exc_value = exc_value

    def clear_exception_values(self):
        """
        Clear values from previous validation
        """
        self.hint = None
        self.exc_text = ''
        self.exc_value = None

    def __call__(self, event, hint):
        """
        Workaround to prevent certain exceptions to be sent to sentry.io
        See: https://github.com/getsentry/sentry-python/issues/149#issuecomment-434448781
        """
        self.clear_exception_values()
        self.init_exception_values(event, hint)

        ignore_event = False
        for rule in settings.EOX_CORE_SENTRY_IGNORED_ERRORS:
            ignore_event = self.validate_single_ignore_rule(rule)
            # If the event meet the conditions to be ignored, break the loop
            if ignore_event:
                return None

        return event

    def validate_single_ignore_rule(self, rule):
        """
        Validates if a given ignored exception rule matches the current exception
        """
        for key, value in six.iteritems(rule):
            # Try to get the validation method based on the current key of the rule
            validate_method = self.validation_exc_methods.get(key, None)
            # If validate_method is not defined, return False
            if not validate_method:
                return False
            result = getattr(self, validate_method)(value)
            if not result:
                return False

        return True

    def validate_exc_class(self, exc_class_path):
        """
        Validate if the current exception object is an instance of the class specified
        on the given path
        """
        exc_class = type(None)
        try:
            exc_class = load_class(exc_class_path)
        except Exception:  # pylint: disable=broad-except
            pass

        return isinstance(self.exc_value, exc_class)

    def validate_exc_text(self, exc_text_expr):
        """
        Validate if any of the given regex matches with the current exception last
        traceback text
        """
        if not isinstance(exc_text_expr, list):
            exc_text_expr = [exc_text_expr]

        for expr in exc_text_expr:
            if re.search(expr, self.exc_text):
                return True

        return False
