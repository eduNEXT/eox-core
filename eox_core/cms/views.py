# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from eox_core.edxapp_wrapper.edxmako_module import render_to_response


@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def simple_view(request):
    """
    Renders simple React js view.
    """

    return render_to_response(u'management.html', {'user': request.user})
