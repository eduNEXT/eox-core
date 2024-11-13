""" Utils for testing"""
from datetime import datetime

import factory
from django.contrib.auth.models import User

DEFAULT_PASSWORD = 'test'


class SuperUserFactory(factory.django.DjangoModelFactory):
    """
    A Factory for User objects.
    """
    class Meta:
        """ Meta """
        model = User
        django_get_or_create = ('email', 'username')

    _DEFAULT_PASSWORD = 'test'

    username = factory.Sequence(lambda n: f'robot{n}')
    email = factory.Sequence(lambda n: f'robot+test+{n}@example.com')
    password = factory.PostGenerationMethodCall(
        'set_password', _DEFAULT_PASSWORD)
    first_name = factory.Sequence(lambda n: f'Robot{n}')
    last_name = 'Test'
    is_staff = True
    is_active = True
    is_superuser = True
    last_login = datetime(2012, 1, 1)
    date_joined = datetime(2011, 1, 1)


class TestStorage:
    """
    This is a storage used for testing purposes
    """
    def url(self, name):
        """
        return the name of the asset
        """
        return name
