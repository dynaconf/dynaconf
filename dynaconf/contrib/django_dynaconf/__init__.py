# WARNING: THIS EXTENSION IS DEPRECATED
# Read more on how to integrate with django on
# https://dynaconf.readthedocs.io/en/latest/guides/django.html
"""Dynaconf django extension

In the `django_project/settings.py` put as 1st app::

    INSTALLED_APPS = [
        'dynaconf.contrib.django_dynaconf',
        ...
    ]

It must be included as the first application on the INSTALLED_APPS list.

Now in the root of your Django project
(the same folder where manage.py is located)

Put your config files `settings.{py|yaml|toml|ini|json}`
and or `.secrets.{py|yaml|toml|ini|json}`

On your projects root folder now you can start as::

    DJANGO_DEBUG='@bool false' \
    DJANGO_ALLOWED_HOSTS='@json ["localhost"]' \
    python manage.py runserver
"""
import sys
import warnings

from django import conf

from .dynaconf_django_conf import settings


warnings.warn(
    "Django Integration for Dynaconf has been updated "
    "you are still using the old style which is deprecated "
    "please upgrade the django integration "
    "read more in https://dynaconf.readthedocs.io/en/latest/guides/django.html"
)


class Wrapper(object):
    def __getattribute__(self, name):
        if name == "settings":
            return settings
        else:
            return getattr(conf, name)


# This implementation is recommended by Guido Van Rossum
# https://mail.python.org/pipermail/python-ideas/2012-May/014969.html
sys.modules["django.conf"] = Wrapper()
