from __future__ import annotations

from django.conf import settings
from django.test import TestCase

# Create your tests here.


class SettingsTest(TestCase):
    def test_settings(self):
        self.assertEqual(settings.SERVER, "prodserver.com")
        self.assertEqual(
            settings.STATIC_URL, "/changed/in/settings.toml/by/dynaconf/"
        )
        self.assertEqual(settings.USERNAME, "admin_user_from_env")
        self.assertEqual(settings.PASSWORD, "My5up3r53c4et")
        self.assertEqual(settings.get("PASSWORD"), "My5up3r53c4et")
        self.assertEqual(settings.FOO, "It overrides every other env")

        with settings.using_env("development"):
            self.assertEqual(settings.SERVER, "devserver.com")
            self.assertEqual(settings.PASSWORD, False)
            self.assertEqual(settings.USERNAME, "admin_user_from_env")
            self.assertEqual(settings.FOO, "It overrides every other env")

        self.assertEqual(settings.SERVER, "prodserver.com")
        self.assertEqual(settings.PASSWORD, "My5up3r53c4et")
        self.assertEqual(settings.USERNAME, "admin_user_from_env")
        self.assertEqual(settings.FOO, "It overrides every other env")

        with settings.using_env("staging"):
            self.assertEqual(settings.SERVER, "stagingserver.com")
            self.assertEqual(settings.PASSWORD, False)
            self.assertEqual(settings.USERNAME, "admin_user_from_env")
            self.assertEqual(settings.FOO, "It overrides every other env")

        self.assertEqual(settings.SERVER, "prodserver.com")
        self.assertEqual(settings.PASSWORD, "My5up3r53c4et")
        self.assertEqual(settings.USERNAME, "admin_user_from_env")
        self.assertEqual(settings.FOO, "It overrides every other env")

        with settings.using_env("customenv"):
            self.assertEqual(settings.SERVER, "customserver.com")
            self.assertEqual(settings.PASSWORD, False)
            self.assertEqual(settings.USERNAME, "admin_user_from_env")
            self.assertEqual(settings.FOO, "It overrides every other env")

        self.assertEqual(settings.SERVER, "prodserver.com")
        self.assertEqual(settings.PASSWORD, "My5up3r53c4et")
        self.assertEqual(settings.USERNAME, "admin_user_from_env")
        self.assertEqual(settings.FOO, "It overrides every other env")
