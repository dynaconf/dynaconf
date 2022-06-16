from __future__ import annotations

from dynaconf import settings


def test_has_wrapped():
    assert settings.configured is True
