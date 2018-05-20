from django.conf import settings
from django.test import TestCase

# Create your tests here.


class SettingsTest(TestCase):

    def test_settings(self):
        self.assertEqual(settings.SERVER, 'dev_server_fromenv.com')
        self.assertEqual(
            settings.STATIC_URL, '/changed/in/settings.toml/by/dynaconf/')
        self.assertEqual(settings.USERNAME, 'dev user')
        self.assertEqual(settings.PASSWORD, 'My5up3r53c4et')
