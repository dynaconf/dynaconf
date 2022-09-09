from __future__ import annotations

import os

from dynaconf import settings

# This is the main settings file
os.environ["SETTINGS_FILE_FOR_DYNACONF"] = "default.toml"


# To make dynaconf read more file we need to include it
print("using config 1")
os.environ["INCLUDES_FOR_DYNACONF"] = "./cfg/settings.toml"

print("development")
settings.setenv("development")
print(settings.VAR_DFT)
print(settings.VAR1)
assert settings.VAR_DFT == "default_dev"
assert settings.VAR1 == "config1_dev"

print("changing to production")
settings.setenv("production")
print(settings.VAR_DFT)
print(settings.VAR1)
assert settings.VAR_DFT == "default_prod"
assert settings.VAR1 == "config1_prod"

print("----")


# To make dynaconf a different file we need to include it
# includes can be a toml-like list
print("using config 2")
os.environ["INCLUDES_FOR_DYNACONF"] = "['./cfg2/settings.toml']"
# if it is done during a running process we need to reload to read the new
# envvar
settings.reload()


print("development")
settings.setenv("development")
print(settings.VAR_DFT)
print(settings.VAR1)
assert settings.VAR_DFT == "default_dev"
assert settings.VAR1 == "config2_dev"

print("changing to production")
settings.setenv("production")
print(settings.VAR_DFT)
print(settings.VAR1)
assert settings.VAR_DFT == "default_prod"
assert settings.VAR1 == "config2_prod"
