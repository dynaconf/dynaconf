from os import environ

from dotenv import cli as dotenv_cli

from dynaconf.utils.parse_conf import parse_conf_data

IDENTIFIER = "env"


def load(obj, env=None, silent=True, key=None):
    """Loads envvars with prefixes:

    `DYNACONF_` (default global) or `$(ENVVAR_PREFIX_FOR_DYNACONF)_`
    """
    global_env = obj.get("ENVVAR_PREFIX_FOR_DYNACONF")
    if global_env is False or global_env.upper() != "DYNACONF":
        load_from_env(IDENTIFIER + "_global", key, "DYNACONF", obj, silent)

    # Load the global env if exists and overwrite everything
    load_from_env(IDENTIFIER + "_global", key, global_env, obj, silent)


def load_from_env(identifier, key, env, obj, silent):
    env_ = ""
    if env is not False:
        env = env.upper()
        env_ = "{0}_".format(env)
    try:
        if key:
            value = environ.get("{0}{1}".format(env_, key))
            if value:
                obj.logger.debug(
                    "env_loader: loading by key: %s:%s (%s:%s)",
                    key,
                    value,
                    identifier,
                    env,
                )
                obj.set(key, value, loader_identifier=identifier, tomlfy=True)
        else:
            trim_len = len(env_)
            data = {
                key[trim_len:]: parse_conf_data(data, tomlfy=True)
                for key, data in environ.items()
                if key.startswith(env_)
            }
            if data:
                obj.logger.debug(
                    "env_loader: loading: %s (%s:%s)", data, identifier, env
                )
                obj.update(data, loader_identifier=identifier)
    except Exception as e:  # pragma: no cover
        e.message = ("env_loader: Error ({0})").format(str(e))
        if silent:
            obj.logger.error(str(e))
        else:
            raise


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
