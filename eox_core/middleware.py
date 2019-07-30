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
import six

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.http import Http404, HttpResponseRedirect

from eox_core.edxapp_wrapper.configuration_helpers import get_configuration_helper
from eox_core.models import Redirection

from eox_core.utils import cache, fasthash


configuration_helper = get_configuration_helper()  # pylint: disable=invalid-name

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

        path = request.path_info

        for regex, values in six.iteritems(redirects):

            if isinstance(values, dict):
                key = next(iter(values))
            else:
                key = values

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


class RedirectionsMiddleware(object):
    """
    Middleware for Redirecting microsites to other domains or to error pages
    """

    def process_request(self, request):
        """
        This middleware handles redirections and error pages according to the
        business logic at edunext
        """
        if not settings.FEATURES.get('USE_REDIRECTION_MIDDLEWARE', True):
            return None

        domain = request.META.get('HTTP_HOST', "")

        # First handle the event where a domain has a redirect target
        cache_key = "redirect_cache." + fasthash(domain)
        target = cache.get(cache_key)  # pylint: disable=maybe-no-member

        if not target:
            try:
                target = Redirection.objects.get(domain__iexact=domain)  # pylint: disable=no-member
            except Redirection.DoesNotExist:  # pylint: disable=no-member
                target = '##none'

            cache.set(  # pylint: disable=maybe-no-member
                cache_key, target, 5 * 60
            )

        if target != '##none':
            # If we are already at the target, just return
            if domain == target.target and request.scheme == target.scheme:  # pylint: disable=no-member
                return None

            to_url = '{scheme}://{host}{path}'.format(
                scheme=target.scheme,  # pylint: disable=no-member
                host=target.target,  # pylint: disable=no-member
                path=request.path,  # pylint: disable=no-member
            )

            return HttpResponseRedirect(
                to_url,
                status=target.status,  # pylint: disable=no-member
            )
        return None

    @staticmethod
    @receiver(post_save, sender=Redirection)
    def clear_cache(sender, instance, **kwargs):  # pylint: disable=unused-argument
        """
        Clear the cached template when the model is saved
        """
        cache_key = "redirect_cache." + fasthash(instance.domain)
        cache.delete(cache_key)  # pylint: disable=maybe-no-member
