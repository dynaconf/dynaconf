from __future__ import annotations

from dynaconf import settings

assert settings.FIRST_VAR == "first_value"
assert settings.SECOND_VAR == "second_value"
assert settings.EXTRA_VAR == "extra_value"
