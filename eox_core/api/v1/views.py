"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_oauth.authentication import OAuth2Authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication



class EdxappUser(APIView):
    """
    Handles API requests to create users
    """

    def get(self, request, *args, **kwargs):
        """
        """
        return Response({"detail": _("ok")}, status=status.HTTP_200_OK)


class UserInfo(APIView):
    """
    Auth-only view to check some basic info about the current user
    Can use Oauth2/Session/JWT authentication
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication, JSONWebTokenAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer)

    def get(self, request, format=None):
        content = {
            # `django.contrib.auth.User` instance.
            'user': unicode(request.user.username),
            'email': unicode(request.user.email),
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'auth': unicode(request.auth)
        }
        return Response(content)
