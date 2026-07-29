from __future__ import annotations

from django.conf import settings
from django.test import TestCase


class SettingsSetVisibilityTest(TestCase):
    """settings.set() values must be visible through django.conf.settings.

    Simulates the pulpcore+rpm pattern: core sets computed values via
    settings.set(), plugin reads them via django.conf.settings.
    """

    def test_module_constant_visible(self):
        self.assertEqual(settings.API_ROOT, "/api/v3/")

    def test_settings_set_value_visible(self):
        self.assertEqual(settings.API_ROOT_NO_FRONT_SLASH, "api/v3/")
