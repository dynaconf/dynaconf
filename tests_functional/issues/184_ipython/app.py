from __future__ import annotations

from dynaconf import settings

print(settings.ENV_FOR_DYNACONF)

assert settings.ENV_FOR_DYNACONF == "WORKS_ON_PYTHON_AND_IPYTHON"
