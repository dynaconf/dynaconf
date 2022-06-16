from __future__ import annotations

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MY_APP",
    merge_enabled=True,
    environments=True,
    env="development",
    settings_files=["settings.yaml"],
    load_dotenv=True,
    ignore_unknown_envvars=True,
)


assert settings.foo == "foo"
assert settings.param_1 == "my_param1"
assert settings.docker.param_2 == "my_param2", settings.docker.param_2
assert settings.docker.param_3 == "my_param3", settings.docker.param_3
