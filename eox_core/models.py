# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


PERMISSIONS = {
    'ANYTHING': 'anything',
    'CREATE_USERS': 'create users',
    'ACTIVATE_USERS': 'activate users',
    'ENROLL_USERS': 'enroll users',
}

# from users.models import User


class EoxData(models.Model):
    """Define the extra fields related to User here"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def for_user(self, u):
        try:
            return EoxData.get(user=u)
        except ObjectDoesNotExist:
            return None

    def user_can(self, action, site):
        # siteobj = EoxSite.objects.filter(site=site)
        # EoxSite.objects.filter(site=site)
        permissions = EoxPermissions.objects.filter(
            oexdata=self, permission=action, site=site)

        if len(permissions) == 0:
            permissions = EoxPermissions.objects.filter(
                oexdata=self, permission=PERMISSIONS.ANYTHING, site=site)

        return len(permissions) > 0


class EoxSite(models.Model):
    site = models.CharField(max_length=2083, unique=True)


class EoxPermissions(models.Model):
    choices = [(x, y) for x, y in PERMISSIONS.items()]
    permission = models.CharField(
        EoxData, choices=choices, max_length=100)
    eoxdata = models.ForeignKey(
        EoxData, on_delete=models.CASCADE, related_name="permissions")
    site = models.ForeignKey(
        EoxSite, on_delete=models.CASCADE, to_field='site')
