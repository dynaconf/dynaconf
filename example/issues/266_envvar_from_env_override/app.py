from __future__ import annotations

from dynaconf import settings

print(f"Current env: {settings.current_env}")

print(f"Dev is: {settings.THISIS}")

print(f"Production is: {settings.from_env('production').THISIS}")

assert settings.THISIS == "development"
assert settings.from_env("production").THISIS == "production"
