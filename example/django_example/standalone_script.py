# You should start your standalone scripts with this:
from __future__ import annotations

from django.conf import settings

# This `DYNACONF.configure()` line may be useful in some cases
# It forces the load of settings
# settings.DYNACONF.configure()

# Now you have access to:

# Django normal settings
print(settings.BASE_DIR)
print(settings.DATABASES)

# Dynaconf methods
print(settings.current_env)
print(settings.get("BASE_DIR"))
print(settings.get("DATABASES.default.ENGINE"))
print(settings.DATABASES.default.ENGINE)

# App settings (defined in `settings.yaml`)
print(settings.SERVER)

# App settings (exported as environment variables)

# `export DJANGO_USERNAME=`
print(settings.USERNAME)

# `export DJANGO_ENVVAR=`
print(settings.ENVVAR)


# test case
expected = {
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    },
    "current_env": "PRODUCTION",
    "DATABASES.DEFAULT.ENGINE": "django.db.backends.sqlite3",
    "SERVER": "prodserver.com",
    "USERNAME": "admin_user_from_env",
    "ENVVAR": "this value exists only in .env",
}

for k, v in expected.items():
    print("Is", k, "equals", v, "?")
    if k.isupper():
        assert settings.get(k) == v
    else:
        assert getattr(settings, k) == v
