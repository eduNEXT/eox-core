# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.http import HttpResponse

import eox_core


def default_view(request):
    response_data = {
        "version": eox_core.__version__,
        "name": "eox-core",
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")
