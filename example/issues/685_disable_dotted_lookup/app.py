from __future__ import annotations

import yaml

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="settings.yaml", environments=True, DOTTED_LOOKUP=False
)

assert settings.get("www.google.com") == "data", settings.get("www.google.com")
assert settings.as_dict() == {"WWW.GOOGLE.COM": "data"}, settings.as_dict()
