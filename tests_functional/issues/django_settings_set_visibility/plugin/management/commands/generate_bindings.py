"""Simulates pulpcore-manager openapi --bindings --component rpm.

Accesses computed settings via django.conf.settings, the same way
rpm plugin code does.
"""
import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Simulates openapi bindings generation accessing computed settings"

    def handle(self, *args, **options):
        result = {
            "settings_type": type(settings).__name__,
            "api_root_no_front_slash": settings.API_ROOT_NO_FRONT_SLASH,
        }

        # Respect django lazy checks, as if we have not intercepted it
        try:
            result["secret_via_get"] = settings.get("SECRET_KEY")
        except ImproperlyConfigured:
            result["secret_via_get"] = "ImproperlyConfigured"

        try:
            result["secret_via_attr"] = settings.SECRET_KEY
        except ImproperlyConfigured:
            result["secret_via_attr"] = "ImproperlyConfigured"

        self.stdout.write(json.dumps(result))
