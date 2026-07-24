"""Reproducer for dynaconf django.conf.settings patch failure.

Simulates the pulpcore+rpm pattern:
- Core settings module has no SECRET_KEY constant (pulpcore 3.115+)
- DjangoDynaconf loads SECRET_KEY from env var
- Core uses post_hooks for computed values after DjangoDynaconf
- Plugin accesses those values via django.conf.settings

Bug: without SECRET_KEY as a module-level constant, dynaconf's load()
step 4 fails to copy Django's built-in settings. This prevents step 5
from patching django.conf.settings, making post_hook values invisible
to code using `from django.conf import settings`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(env_extra=None):
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "core.settings"}
    if env_extra:
        env.update(env_extra)
    if env_extra is None or "DJANGO_SECRET_KEY" not in env_extra:
        env.pop("DJANGO_SECRET_KEY", None)
        env.pop("SECRET_KEY", None)

    result = subprocess.run(
        [sys.executable, "manage.py", "generate_bindings"],
        env=env,
        capture_output=True,
        text=True,
        cwd=HERE,
    )
    assert result.returncode == 0, f"failed:\n{result.stderr}"
    return json.loads(result.stdout)


# Scenario 1: SECRET_KEY provided via env var
data = run(env_extra={"DJANGO_SECRET_KEY": "test-secret-for-ci"})
assert data["settings_type"] == "LazySettings"
assert data["api_root_no_front_slash"] == "api/v3/"
assert data["secret_via_get"] == "test-secret-for-ci"
assert data["secret_via_attr"] == "test-secret-for-ci"

# Scenario 2: no SECRET_KEY anywhere
data = run()
assert data["settings_type"] == "LazySettings"
assert data["api_root_no_front_slash"] == "api/v3/"
assert data["secret_via_get"] == "ImproperlyConfigured"
assert data["secret_via_attr"] == "ImproperlyConfigured"

print("PASS")
