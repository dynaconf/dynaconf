from django.conf import settings
from django.test import TestCase

# Create your tests here.


class TestSettingsMerged(TestCase):
    def test_settings_merged_correctly_with_populate_obj(self):
        self.assertEqual(
            settings.INSTALLED_APPS,
            [
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "newapp",
            ],
        )
        self.assertEqual(settings.PERSON, {"name": "Bruno", "age": 17})
        # not uniquely merged
        self.assertEqual(
            settings.FRUITS,
            ["banana", "apple", "watermelon", "banana", "grapes"],
        )
        # banana does not repeat
        self.assertEqual(
            settings.UNIQUE_FRUITS, ["apple", "watermelon", "banana", "grapes"]
        )
