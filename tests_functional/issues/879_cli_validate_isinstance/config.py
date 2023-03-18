from __future__ import annotations

from dynaconf import Dynaconf

# this settings should output validate only`
settings_noenvs = Dynaconf(settings_file="settings-no-envs.toml")
settings_envs = Dynaconf(environments=True, settings_file="settings-envs.toml")

# this settings should output the proper validation error
settings_noenvs_invalid = Dynaconf(
    settings_file="settings-no-envs-invalid.toml"
)
settings_envs_invalid = Dynaconf(
    environments=True, settings_file="settings-envs-invalid.toml"
)
