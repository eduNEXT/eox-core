"""
Custom authenticators for the Support V1 API.
"""
import time

import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework import authentication
from rest_framework.authentication import get_authorization_header


class JWTsignedOauthAppAuthentication(authentication.BaseAuthentication):
    """
    Authentication class to verify JWTs signed by trusted services.
    Allows authentication for the OauthApplicationAPIView in Open edX.
    """

    def authenticate(self, request):
        """
        Extracts the JWT token from the Authorization header and verifies it.
        If authentication fails, it does NOT raise an exception to allow
        other authentication classes to attempt authentication.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) != 2:
            return None

        token = auth[1]
        return self.authenticate_token(token)

    def authenticate_token(self, token):
        """
        Attempts to authenticate the JWT token. If verification fails,
        returns None instead of raising an exception, allowing other authentication
        classes to handle authentication.
        """
        try:
            decoded_payload = jwt.decode(
                token,
                settings.EOX_CORE_JWT_SIGNED_OAUTH_APP_PUBLIC_KEY,
                algorithms=["RS256"]
            )

            if decoded_payload["exp"] < time.time():
                return None

            return (AnonymousUser(), None)

        except (ExpiredSignatureError, InvalidTokenError):
            return None
