from __future__ import annotations

from dynaconf import settings
from dynaconf.utils.inspect import get_history

with open(settings.find_file("settings.sff")) as settings_file:
    print("settings from sff file\n", settings_file.read())

assert settings.NAME == "Bruno Rocha"
assert settings.EMAIL == "bruno@rocha.com.from_env"

print("Name is:", settings.NAME)
print("Email is:", settings.EMAIL)

print(settings.get_fresh("NAME"))

# Assure new inspect/history works properly
history = get_history(settings, "NAME")
assert history[0]["loader"] == "sff"
assert history[0]["value"] == "Bruno Rocha"
