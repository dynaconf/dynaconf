from __future__ import annotations

from dynaconf import settings

print("EXAMPLE_ prefix")
settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="EXAMPLE")
print(settings.VAR1)
print(settings.VAR2)

print("_ prefix")
settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="")
print(settings.VAR1)
print(settings.VAR2)

print("no prefix at all")
settings.configure(ENVVAR_PREFIX_FOR_DYNACONF=False)
print(settings.VAR1)
print(settings.VAR2)


# test issue 166 (renamed GLOBAL_ENV_)
print("using GLOBAL_ENV_")
settings.configure(GLOBAL_ENV_FOR_DYNACONF=False)
print(settings.VAR1)
print(settings.VAR2)
