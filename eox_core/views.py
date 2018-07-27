# -*- coding: utf-8 -*-
"""The views for the exc-core plugin project"""
from __future__ import unicode_literals

import json
from subprocess import check_output

from django.http import HttpResponse
from django.shortcuts import render

import eox_core


def default_view(request):
    """
    The HTTP endopoint to get the eox-core API version
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
