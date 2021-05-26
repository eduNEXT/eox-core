"""Wrapper file for eox-audit-model"""
from importlib import import_module, util

try:
    eox_audit_decorator = import_module('eox_audit_model.decorators')
    audit_method = eox_audit_decorator.audit_method
except ImportError:
    pass


def audit_api_wrapper(action='', data_filter=None):
    """This decorator wraps the functionality of audit_method in order to
    work with django API view methods,also this allows to filter the data that will be
    stored in the data base.

    Example

    class YourAPIView(APIView):

        @audit_api_wrapper(action='Get my items', data_filter=['username', 'location'])
        def get(self, request, *args, **kwargs):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not util.find_spec('eox_audit_model'):
                return func(*args, **kwargs)

            request = args[1]
            audit_data = request.data if request.data else request.query_params

            if data_filter:
                audit_data = {key: value for key, value in audit_data.items() if key in data_filter}

            @audit_method(action=action)
            def eox_core_api_method(audit_data):
                """This method is just a wrapper in order to capture the input data"""
                return func(*args, **kwargs)

            return eox_core_api_method(audit_data)

        return wrapper

    return decorator
