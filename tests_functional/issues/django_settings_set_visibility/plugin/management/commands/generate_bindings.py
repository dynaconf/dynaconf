"""Simulates pulpcore-manager openapi --bindings --component rpm.

Accesses computed settings via django.conf.settings, the same way
rpm plugin code does.
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from dynaconf import Dynaconf

class Command(BaseCommand):
    help = "Simulates openapi bindings generation accessing computed settings"

    def handle(self, *args, **options):
        assert isinstance(settings, Dynaconf), f"{type(settings)=}"
        root = settings.API_ROOT_NO_FRONT_SLASH
        self.stdout.write(f"API_ROOT_NO_FRONT_SLASH={root}")
