# -*- coding: utf-8 -*-
"""The views for the exc-core plugin project"""
from __future__ import unicode_literals

import json

from django.http import HttpResponse

import eox_core


def default_view(request):
    """
    The HTTP endopoint to get the eox-core API version
    """
    response_data = {
        "version": eox_core.__version__,
        "name": "eox-core",
    }
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )
