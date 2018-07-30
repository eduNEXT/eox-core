
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from datetime import datetime
from pytz import UTC

DEFAULT_PASSWORD = 'test'

class SuperUserFactory(DjangoModelFactory):
    """
    A Factory for User objects.
    """
    class Meta(object):
        model = User
        django_get_or_create = ('email', 'username')

    _DEFAULT_PASSWORD = 'test'

    username = factory.Sequence(u'robot{0}'.format)
    email = factory.Sequence(u'robot+test+{0}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD)
    first_name = factory.Sequence(u'Robot{0}'.format)
    last_name = 'Test'
    is_staff = True
    is_active = True
    is_superuser = True
    last_login = datetime(2012, 1, 1, tzinfo=UTC)
    date_joined = datetime(2011, 1, 1, tzinfo=UTC)
