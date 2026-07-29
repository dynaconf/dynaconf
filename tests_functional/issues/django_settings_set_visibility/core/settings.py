"""Simulates pulpcore 3.115+ settings module.

No SECRET_KEY constant — removed as insecure default.
SECRET_KEY is expected via env var (DJANGO_SECRET_KEY through dynaconf).

After DjangoDynaconf loads, computed settings are added via settings.set(),
simulating pulpcore's V3_API_ROOT_NO_FRONT_SLASH pattern.
"""

import os

import dynaconf  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "plugin",
]

ROOT_URLCONF = "core.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

API_ROOT = "/api/v3/"


def hook_fn(settings):
    return {"API_ROOT_NO_FRONT_SLASH": settings.API_ROOT.lstrip("/")}


settings = dynaconf.DjangoDynaconf(
    __name__,
    post_hooks=hook_fn,
)
