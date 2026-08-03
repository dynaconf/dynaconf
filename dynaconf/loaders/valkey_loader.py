from __future__ import annotations

from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import build_env_list
from dynaconf.utils import upperfy
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.utils.parse_conf import unparse_conf_data

try:
    from valkey import Valkey
except ImportError:
    Valkey = None

IDENTIFIER = "valkey"


def _get_valkey_client(obj):
    """Create a Valkey client from settings.

    If VALKEY_URL_FOR_DYNACONF is set, uses Valkey.from_url() which
    supports all URL schemes including valkeys:// for TLS connections.
    Otherwise falls back to creating a client from VALKEY_FOR_DYNACONF kwargs.

    :param obj: the settings instance
    :return: Valkey client
    """
    if Valkey is None:
        raise ImportError(
            "valkey package is not installed in your environment. "
            "`pip install dynaconf[valkey]` or disable the valkey loader with "
            "export VALKEY_ENABLED_FOR_DYNACONF=false"
        )

    valkey_url = obj.get("VALKEY_URL_FOR_DYNACONF")
    if valkey_url:
        return Valkey.from_url(valkey_url)
    return Valkey(**obj.get("VALKEY_FOR_DYNACONF"))


def load(obj, env=None, silent=True, key=None, validate=False):
    """Reads and loads in to "settings" a single key or all keys from valkey

    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """
    valkey = _get_valkey_client(obj)
    prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF")
    env_list = build_env_list(obj, env or obj.current_env)
    # prefix is added to env_list to keep backwards compatibility
    if prefix:
        env_list.insert(0, prefix)

    for env_name in env_list:
        if prefix:
            holder = f"{prefix.upper()}_{env_name.upper()}"
        else:
            holder = env_name.upper()

        try:
            source_metadata = SourceMetadata(IDENTIFIER, "unique", env_name)
            if key:
                value = valkey.hget(holder.upper(), key)
                if value:
                    parsed_value = parse_conf_data(
                        value, tomlfy=True, box_settings=obj
                    )
                    if parsed_value:
                        obj.set(
                            key,
                            parsed_value,
                            validate=validate,
                            loader_identifier=source_metadata,
                        )
            else:
                data = {
                    key: parse_conf_data(value, tomlfy=True, box_settings=obj)
                    for key, value in valkey.hgetall(holder.upper()).items()
                }
                if data:
                    obj.update(
                        data,
                        loader_identifier=source_metadata,
                        validate=validate,
                    )
        except Exception:
            if silent:
                return False
            raise


def write(obj, data=None, **kwargs):
    """Write a value in to loader source

    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    if obj.VALKEY_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError(
            "Valkey is not configured \n"
            "export VALKEY_ENABLED_FOR_DYNACONF=true\n"
            "and configure the VALKEY_*_FOR_DYNACONF variables"
        )
    client = _get_valkey_client(obj)
    holder = obj.get("ENVVAR_PREFIX_FOR_DYNACONF").upper()
    # add env to holder
    holder = f"{holder}_{obj.current_env.upper()}"

    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError("Data must be provided")
    valkey_data = {
        upperfy(key): unparse_conf_data(value) for key, value in data.items()
    }
    client.hset(holder.upper(), mapping=valkey_data)
    load(obj)


def delete(obj, key=None):
    """
    Delete a single key if specified, or all env if key is none
    :param obj: settings object
    :param key: key to delete from store location
    :return: None
    """
    client = _get_valkey_client(obj)
    holder = obj.get("ENVVAR_PREFIX_FOR_DYNACONF").upper()
    # add env to holder
    holder = f"{holder}_{obj.current_env.upper()}"

    if key:
        client.hdel(holder.upper(), upperfy(key))
        obj.unset(key)
    else:
        keys = client.hkeys(holder.upper())
        client.delete(holder.upper())
        obj.unset_all(keys)
