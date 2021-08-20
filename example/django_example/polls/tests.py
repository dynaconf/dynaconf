from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

# Create your tests here.


@override_settings(ISSUE=596)
class SettingsTest(TestCase):
    def test_settings(self):
        self.assertEqual(settings.ISSUE, 596)
        self.assertEqual(settings.SERVER, "prodserver.com")
        # self.assertEqual(
        #     settings.STATIC_URL, "/changed/in/settings.toml/by/dynaconf/"
        # )
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

    def test_override_settings_context(self):
        self.assertEqual(settings.ISSUE, 596)
        with self.settings(DAY=19):
            self.assertEqual(settings.DAY, 19)


assert settings.TEST_VALUE == "a"


@override_settings(TEST_VALUE="c")
class TestOverrideClassDecoratorAndManager(TestCase):
    def test_settings(self):
        self.assertEqual(settings.TEST_VALUE, "c")

    def test_modified_settings(self):
        with self.settings(TEST_VALUE="b"):
            self.assertEqual(settings.TEST_VALUE, "b")


class TestNoOverride(TestCase):
    def test_settings(self):
        self.assertEqual(settings.TEST_VALUE, "a")


class TestModifySettingsContextManager(TestCase):
    def test_settings(self):
        self.assertEqual(settings.COLORS, ["black", "green"])

        with self.modify_settings(
            COLORS={
                "append": ["blue"],
                "prepend": ["red"],
                "remove": ["black"],
            }
        ):
            self.assertEqual(settings.COLORS, ["red", "green", "blue"])
