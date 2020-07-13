""" Backend abstraction """
import os

import edxmako  # pylint: disable=import-error

from eox_core import cms


def render_to_response(template_name, dictionary=None, namespace='main', request=None, **kwargs):
    """ Custom render_to_response implementation using configurable backend and adding template dir """
    module_templates_to_include = [
        cms
    ]
    for module in module_templates_to_include:
        path_to_templates = os.path.dirname(module.__file__) + '/templates'
        if path_to_templates not in edxmako.LOOKUP['main'].directories:
            edxmako.paths.add_lookup('main', path_to_templates)
    return edxmako.shortcuts.render_to_response(template_name, dictionary, namespace, request, **kwargs)
