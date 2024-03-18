from __future__ import annotations

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

assert settings.TEST_VALUE == "a"


@override_settings(TEST_VALUE="c")
class CheckSettings(TestCase):
    def test_settings(self):
        self.assertEqual(settings.TEST_VALUE, "c")

    def test_modified_settings(self):
        with self.settings(TEST_VALUE="b"):
            self.assertEqual(settings.TEST_VALUE, "b")
