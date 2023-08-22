from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="settings.toml",
    load_dotenv=True,
)


# TOML must rely on its own type system
assert settings.TOMLUPPERTRUE == "True"
assert settings.TOMLUPPERFALSE == "False"
assert settings.TOMLLOWERTRUE is True
assert settings.TOMLLOWERFALSE is False

# ENV vars must transform `True` to `true` and `False` to `false`
assert settings.UPPERTRUE is True, settings.UPPERTRUE
assert settings.UPPERFALSE is False, settings.UPPERFALSE
assert settings.LOWERTRUE is True, settings.LOWERTRUE
assert settings.LOWERFALSE is False, settings.LOWERFALSE

print("BOOLEAN FIX FOR ENV VARS WORKS")
