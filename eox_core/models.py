# -*- coding: utf-8 -*-
"""Models for the eox-core API"""
from __future__ import unicode_literals


class Authentication(object):
    """ Handle Authentication"""
    pass


class AuthSession(Authentication):
    """ Handle AuthSession"""
    pass


class AuthToken(Authentication):
    """ Handle AuthToken"""
    pass


class AuthOauth(Authentication):
    """ Handle AuthOauth"""
    pass


class AuthCustom(Authentication):
    """ Handle AuthCustom"""
    def validate(self):
        """ Allowed or not """
        return True


class Authorization(object):
    """ Handle Authorization"""
    def __init__(self):
        pass

    def is_authorized(self):
        """ Allowed or not """
        return True
