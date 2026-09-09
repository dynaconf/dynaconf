"""Tests for custom objects implementing the _dynaconf_lazy_format protocol.

Remove in 4.0.0.
"""

import contextlib
from collections.abc import Generator
from typing import Any

import pytest

from dynaconf import Dynaconf
from dynaconf.base import Settings

DIRECT_ATTRIBUTES = ("vault",)


class VaultAwareSettings(Settings):
    """Subclass that stores whitelisted attributes as normal Python attributes,
    bypassing dynaconf's config store."""

    def __getattribute__(self, name: str) -> Any:
        if name in DIRECT_ATTRIBUTES:
            return object.__getattribute__(self, name)
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        if name in DIRECT_ATTRIBUTES:
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)


class FakeFormatter:
    token = "_deferred_ref"


class DeferredValue:
    """Returns itself until a vault backend is attached, then resolves."""

    formatter = FakeFormatter()

    def __init__(self, path: str, key: str):
        self.path = path
        self.key = key

    @property
    def _dynaconf_lazy_format(self) -> bool:
        if getattr(self, "_nonlazy_once", False):
            self._nonlazy_once = False
            return False
        else:
            return True

    def __call__(self, settings: Any):
        try:
            vault = settings.vault
        except AttributeError:
            vault = None
        if vault is None:
            self._nonlazy_once = True
            return self
        return vault[self.path][self.key]


class LazyTemplate:
    """Renders a template string using other settings values."""

    formatter = property(lambda self: self)
    token = "@template"

    def __init__(self, template: str):
        self.template = template
        self._lazy_frozen = False
        self._lazy_frozen_once = False

    @contextlib.contextmanager
    def _freeze_lazy(self) -> Generator[None, None, None]:
        if self._lazy_frozen:
            yield
        else:
            self._lazy_frozen = True
            try:
                yield
            finally:
                self._lazy_frozen = False

    @property
    def _dynaconf_lazy_format(self) -> bool:
        if self._lazy_frozen:
            return False
        elif self._lazy_frozen_once:
            self._lazy_frozen_once = False
            return False
        else:
            return True

    def __call__(self, settings: Any):
        with self._freeze_lazy():
            return self.template.replace("{{APP_NAME}}", settings.APP_NAME)


class TestDeferredValueProtocol:
    @pytest.fixture()
    def settings(self):
        settings = VaultAwareSettings()
        settings.set("DB_PASSWORD", DeferredValue("secrets/db", "password"))
        return settings

    def test_returns_self_when_backend_missing(self, settings):
        for _ in range(5):
            value = settings.DB_PASSWORD
            assert isinstance(value, DeferredValue)

    def test_resolves_after_vault_attached(self, settings):
        settings.vault = {"secrets/db": {"password": "s3cret"}}
        assert settings.DB_PASSWORD == "s3cret"

    def test_not_cached_so_vault_change_visible(self, settings):
        for _ in range(5):
            first = settings.DB_PASSWORD
        assert isinstance(first, DeferredValue)

        settings.vault = {"secrets/db": {"password": "s3cret"}}
        assert settings.DB_PASSWORD == "s3cret"

    def test_multiple_deferred_values_resolve_independently(self, settings):
        settings.set("API_KEY", DeferredValue("secrets/api", "token"))

        for _ in range(5):
            assert isinstance(settings.DB_PASSWORD, DeferredValue)
            assert isinstance(settings.API_KEY, DeferredValue)

        settings.vault = {
            "secrets/db": {"password": "dbpass"},
            "secrets/api": {"token": "tok-123"},
        }
        assert settings.DB_PASSWORD == "dbpass"
        assert settings.API_KEY == "tok-123"


class TestLazyTemplateProtocol:
    @pytest.fixture()
    def settings(self):
        settings = Dynaconf()
        settings.set("APP_NAME", "myapp")
        settings.set("HOSTNAME", LazyTemplate("{{APP_NAME}}.example.com"))
        return settings

    def test_renders_template_with_settings_context(self, settings):
        assert settings.HOSTNAME == "myapp.example.com"

    def test_unfreezes_after_render(self, settings):
        """The freeze flag resets after rendering, so subsequent reads work."""
        first = settings.HOSTNAME
        second = settings.HOSTNAME
        assert first == second == "myapp.example.com"

    def test_reflects_changed_dependency(self):
        settings = Dynaconf()
        settings.set("APP_NAME", "v1")
        settings.set("HOSTNAME", LazyTemplate("{{APP_NAME}}.example.com"))

        assert settings.HOSTNAME == "v1.example.com"

        settings.set("APP_NAME", "v2")
        assert settings.HOSTNAME == "v2.example.com"
