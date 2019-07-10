#!/usr/bin/python
"""
This file implements the Middleware support for the Open edX platform.
A microsite enables the following features:
1) Mapping of sub-domain name to a 'brand', e.g. foo-university.edx.org
2) Present a landing page with a listing of courses that are specific to the 'brand'
3) Ability to swap out some branding elements in the website
"""
import logging
import re

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login

from django.http import Http404, HttpResponseRedirect

from eox_core.edxapp_wrapper.configuration_helpers import get_configuration_helper


configuration_helper = get_configuration_helper()  # pylint: disable=invalid-name

HOST_VALIDATION_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,5})?$")
LOG = logging.getLogger(__name__)


class PathRedirectionMiddleware(object):
    """
    Middleware to create custom responses based on the request path
    """

    def process_request(self, request):
        """
        This middleware processes the path of every request and determines if there
        is a configured action to take.
        """

        if not configuration_helper.has_override_value("EDNX_CUSTOM_PATH_REDIRECTS"):
            return None

        redirects = configuration_helper.get_value("EDNX_CUSTOM_PATH_REDIRECTS", {})

        for regex, values in redirects.iteritems():

            if isinstance(values, dict):
                key = next(iter(values))
            else:
                key = values

            path = request.path_info
            regex_path_match = re.compile(regex.format(
                COURSE_ID_PATTERN=settings.COURSE_ID_PATTERN,
                USERNAME_PATTERN=settings.USERNAME_PATTERN,
            ))

            if regex_path_match.match(path):
                try:
                    action = getattr(self, key)
                    return action(request=request, key=key, values=values, path=path)
                except Http404:  # we expect 404 to be raised
                    raise
                except Exception as error:  # pylint: disable=broad-except
                    LOG.error("The PathRedirectionMiddleware generated an error at: %s%s",
                              request.get_host(),
                              request.get_full_path())
                    LOG.error(error)
                    return None
        return None

    def login_required(self, request, path, **kwargs):  # pylint: disable=unused-argument
        """
        Action: a user session must exist.
        If it does not, redirect to the login page
        """
        if request.user.is_authenticated():
            return None
        resolved_login_url = configuration_helper.get_dict("FEATURES", {}).get(
            "ednx_custom_login_link", settings.LOGIN_URL)
        return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)

    def not_found(self, **kwargs):  # pylint: disable=unused-argument
        """
        Action: return 404 error for anyone
        """
        raise Http404

    def not_found_loggedin(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        Action: return 404 error for users which have a session
        """
        if request.user.is_authenticated():
            raise Http404

    def not_found_loggedout(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        Action: return 404 error for users that don't have a session
        """
        if not request.user.is_authenticated():
            raise Http404

    def redirect_always(self, key, values, **kwargs):  # pylint: disable=unused-argument
        """
        Action: redirect to the given target
        """
        return HttpResponseRedirect(values[key])

    def redirect_loggedin(self, request, key, values, **kwargs):  # pylint: disable=unused-argument
        """
        Action: redirect logged users to the given target
        """
        if request.user.is_authenticated():
            return HttpResponseRedirect(values[key])
        return None

    def redirect_loggedout(self, request, key, values, **kwargs):  # pylint: disable=unused-argument
        """
        Action: redirect external visitors to the given target
        """
        if not request.user.is_authenticated():
            return HttpResponseRedirect(values[key])
        return None
