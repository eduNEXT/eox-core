# -*- coding: utf-8 -*-
"""The generic views for the exc-core plugin project"""

from __future__ import unicode_literals

import json
from os.path import dirname, realpath
from subprocess import check_output

from django.http import HttpResponse


import eox_core


def info_view(request):
    """
    Basic view to show the working version and the exact git commit of the
    installed app
    """
    try:
        working_dir = dirname(realpath(__file__))
        git_data = unicode(check_output(["git", "rev-parse", "HEAD"], cwd=working_dir))
    except Exception:
        git_data = ""

    response_data = {
        "version": eox_core.__version__,
        "name": "eox-core",
        "git": git_data.rstrip('\r\n'),
    }
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )

