from os import environ

from dotenv import cli as dotenv_cli

from dynaconf.utils import upperfy
from dynaconf.utils.parse_conf import parse_conf_data


IDENTIFIER = "env"


def load(obj, env=None, silent=True, key=None):
    """Loads envvars with prefixes:

    `DYNACONF_` (default global) or `$(ENVVAR_PREFIX_FOR_DYNACONF)_`
    """
    global_prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF")
    if global_prefix is False or global_prefix.upper() != "DYNACONF":
        load_from_env(obj, "DYNACONF", key, silent, IDENTIFIER + "_global")

    # Load the global env if exists and overwrite everything
    load_from_env(obj, global_prefix, key, silent, IDENTIFIER + "_global")


def load_from_env(
    obj,
    prefix=False,
    key=None,
    silent=False,
    identifier=IDENTIFIER,
    env=False,  # backwards compatibility bc renamed param
):
    if prefix is False and env is not False:
        prefix = env

    env_ = ""
    if prefix is not False:
        if not isinstance(prefix, str):
            raise TypeError("`prefix/env` must be str or False")

        prefix = prefix.upper()
        env_ = f"{prefix}_"

    if key:
        key = upperfy(key)
        value = environ.get(f"{env_}{key}")
        if value:
            try:  # obj is a Settings
                obj.set(key, value, loader_identifier=identifier, tomlfy=True)
            except AttributeError:  # obj is a dict
                obj[key] = parse_conf_data(
                    value, tomlfy=True, box_settings=obj
                )
    else:
        trim_len = len(env_)
        data = {
            key[trim_len:]: parse_conf_data(
                data, tomlfy=True, box_settings=obj
            )
            for key, data in environ.items()
            if key.startswith(env_)
        }
        if data:
            obj.update(data, loader_identifier=identifier)


def write(settings_path, settings_data, **kwargs):
    """Write data to .env file"""
    for key, value in settings_data.items():
        quote_mode = (
            isinstance(value, str)
            and (value.startswith("'") or value.startswith('"'))
        ) or isinstance(value, (list, dict))
        dotenv_cli.set_key(
            str(settings_path),
            key,
            str(value),
            quote_mode="always" if quote_mode else "none",
        )
