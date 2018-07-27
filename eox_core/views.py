# -*- coding: utf-8 -*-
"""The generic views for the exc-core plugin project"""

from __future__ import unicode_literals

import json
from subprocess import check_output

from django.http import HttpResponse
from django.shortcuts import render

import eox_core


def info_view(request):
    """
    Basic view to show the working version and the exact git commit of the installed app
    """
    try:
        git_data = unicode(check_output(["git", "rev-parse", "HEAD"]))
    except Exception as e:
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
