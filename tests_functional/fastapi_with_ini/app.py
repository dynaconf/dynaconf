from __future__ import annotations

from typing import Optional

from fastapi import FastAPI

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file="config.toml",  # location of config file
    environments=["ansible", "puppet"],  # available modes/environments
    envvar_prefix="TEFLO",  # prefix for exporting env vars
    env_switcher="TEFLO_MODE",  # Variable that controls mode switch
    env="ANSIBLE",  # Initial env/mode
)

app = FastAPI()


@app.get("/settings")
def read_root():
    return settings


@app.get("/settings/{setting_name}")
def read_item(setting_name: str):
    return {setting_name: settings.setting_name}


if settings.current_env == "ANSIBLE":  # this is the initial default
    assert settings.data_folder == "ansible/.teflo"

if settings.current_env == "PUPPET":  # only when TEFLO_MODE=puppet
    assert settings.data_folder == "puppet/.teflo"

assert settings.log_level == "info"  # might be exported TEFLO_DEBUG_MODE

assert settings.workspace == "."

print(settings.data_folder)
print(settings["log_remove"])
print(settings.get("verbosity"))
print(settings.LOG_LEVEL)
