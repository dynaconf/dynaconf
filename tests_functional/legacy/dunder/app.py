from __future__ import annotations

from pprint import pprint

from dynaconf import settings

settings.FILES

keys = ["default", "env", "py"]

pprint(settings.FILES)
for key in keys:
    assert settings.FILES.loaded.TYPES[key] is True
    assert settings.FILES.loaded["TYPES"][key] is True

    assert key in settings.FILES.all
    assert key in settings.FILES["all"]

assert settings.FILES.last == ["env"]
assert "nothere" not in settings.FILES
print(settings.FILES)
