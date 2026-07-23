"""Reproducer for dynaconf django.conf.settings patch failure.

Simulates the pulpcore+rpm pattern:
- Core settings module has no SECRET_KEY constant (pulpcore 3.115+)
- DjangoDynaconf loads SECRET_KEY from env var
- Core uses settings.set() for computed values after DjangoDynaconf
- Plugin accesses those values via django.conf.settings

Bug: without SECRET_KEY as a module-level constant, dynaconf's load()
step 4 fails to copy Django's built-in settings. This prevents step 5
from patching django.conf.settings, making settings.set() values
invisible to code using `from django.conf import settings`.

With DJANGO_SECRET_KEY in env: step 5 runs, patching works, PASS.
Without SECRET_KEY: step 5 doesn't run, patching broken, FAIL with
  AttributeError: 'Settings' object has no attribute '...'
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(description, env_extra=None):
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "core.settings"}
    if env_extra:
        env.update(env_extra)
    # Remove any leftover SECRET_KEY unless explicitly provided
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
    if result.returncode != 0:
        print(f"FAIL: {description}")
        print(f"  stderr: {result.stderr.strip()}")
        return False
    print(f"PASS: {description}")
    print(f"  stdout: {result.stdout.strip()}")
    return True


passed = True

# Scenario 1: SECRET_KEY via env var, settings.set() values visible.
# Proves the test infrastructure works (pulpcore with PULP_SECRET_KEY set).
if not run(
    "SECRET_KEY via env var, settings.set() visible through django.conf",
    env_extra={"DJANGO_SECRET_KEY": "test-secret-for-ci"},
):
    passed = False

# Scenario 2: No SECRET_KEY in module or env.
# dynaconf should still patch django.conf.settings (step 5) so that
# settings.set() values are visible to plugin code.
# Currently fails: AttributeError on the computed setting.
if not run(
    "no SECRET_KEY, settings.set() values still visible through django.conf",
):
    passed = False

if not passed:
    sys.exit(1)
