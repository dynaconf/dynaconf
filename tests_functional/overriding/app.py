from __future__ import annotations

from dynaconf import settings

assert settings.REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES == [
    "rest_framework.authentication.SessionAuthentication",
    # user_settings.py will remove the line below
    # 'pulpcore.app.authentication.PulpRemoteUserAuthentication',
    "rest_framework.authentication.BasicAuthentication",
], settings.REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES
