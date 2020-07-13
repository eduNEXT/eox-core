# -*- coding: utf-8 -*-
""" Admin.py """
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from eox_core.edxapp_wrapper.users import get_login_failures, get_user_signup_source
from eox_core.models import Redirection

LoginFailures = get_login_failures()  # pylint: disable=invalid-name
UserSignupSource = get_user_signup_source()  # pylint: disable=invalid-name


class UserSignupSourceAdmin(admin.ModelAdmin):
    """ Admin interface for the UserSignupSource model. """
    list_display = ('user', 'site')
    list_per_page = 20
    raw_id_fields = ('user',)
    search_fields = ('site', 'user__username', 'user__email',)
    # Prevent expensive duplicated COUNT query
    show_full_result_count = False


class LoginFailuresAdmin(admin.ModelAdmin):
    """ Admin interface for the LoginFailures model. """
    list_display = ('user', 'failure_count', 'lockout_until',)
    search_fields = ('user__username', 'user__email',)
    # Prevent expensive duplicated COUNT query
    show_full_result_count = False


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


try:
    admin.site.register(LoginFailures, LoginFailuresAdmin)
except AlreadyRegistered:
    pass

try:
    admin.site.register(UserSignupSource, UserSignupSourceAdmin)
except AlreadyRegistered:
    pass

admin.site.register(Redirection, RedirectionAdmin)
