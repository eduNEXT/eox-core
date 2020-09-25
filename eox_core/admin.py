# -*- coding: utf-8 -*-
""" Admin.py """
from __future__ import unicode_literals

from django.contrib import admin

from eox_core.models import Redirection


class RedirectionAdmin(admin.ModelAdmin):
    """
    Admin view to see and edit edunext redirection objects.
    """
    list_display = [
        'target',
        'domain',
        'scheme',
    ]
    search_fields = ('target', 'domain',)


admin.site.register(Redirection, RedirectionAdmin)
