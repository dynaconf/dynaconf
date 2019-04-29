# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac
from dynaconf.utils.parse_conf import parse_conf_data

try:
    from hvac import Client
except ImportError:
    raise ImportError(
        "vault package is not installed in your environment. "
        "`pip install dynaconf[vault]` or disable the vault loader with "
        "export VAULT_ENABLED_FOR_DYNACONF=false"
    )


IDENTIFIER = "vault"


def _get_env_list(obj, env):
    """Creates the list of environments to read

    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :return: a list of working environments
    """
    # add the [default] env
    env_list = [obj.get("DEFAULT_ENV_FOR_DYNACONF")]
    # compatibility with older versions that still uses [dynaconf] as
    # [default] env
    global_env = obj.get("ENVVAR_PREFIX_FOR_DYNACONF") or "DYNACONF"
    if global_env not in env_list:
        env_list.append(global_env)
    # add the current env
    if obj.current_env and obj.current_env not in env_list:
        env_list.append(obj.current_env)
    # add a manually set env
    if env and env not in env_list:
        env_list.append(env)
    # add the [global] env
    env_list.append("GLOBAL")
    return [env.lower() for env in env_list]


def get_client(obj):
    client = Client(
        **{k: v for k, v in obj.VAULT_FOR_DYNACONF.items() if v is not None}
    )
    assert (
        client.is_authenticated()
    ), "Vault authentication error is VAULT_TOKEN_FOR_DYNACONF defined?"
    return client


def load(obj, env=None, silent=None, key=None):
    """Reads and loads in to "settings" a single key or all keys from vault

    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """

    client = get_client(obj)
    env_list = _get_env_list(obj, env)
    for env in env_list:
        path = "/".join([obj.VAULT_PATH_FOR_DYNACONF, env]).replace("//", "/")
        data = client.read(path)
        if data:
            # There seems to be a data dict within a data dict,
            # extract the inner data
            data = data.get("data", {}).get("data", {})
        try:
            if data and key:
                value = parse_conf_data(data.get(key), tomlfy=True)
                if value:
                    obj.logger.debug(
                        "vault_loader: loading by key: %s:%s (%s:%s)",
                        key,
                        "****",
                        IDENTIFIER,
                        path,
                    )
                    obj.set(key, value)
            elif data:
                obj.logger.debug(
                    "vault_loader: loading: %s (%s:%s)",
                    list(data.keys()),
                    IDENTIFIER,
                    path,
                )
                obj.update(data, loader_identifier=IDENTIFIER, tomlfy=True)
        except Exception as e:
            if silent:
                if hasattr(obj, "logger"):
                    obj.logger.error(str(e))
                return False
            raise


def write(obj, data=None, **kwargs):
    """Write a value in to loader source

    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    if obj.VAULT_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError(
            "Vault is not configured \n"
            "export VAULT_ENABLED_FOR_DYNACONF=true\n"
            "and configure the VAULT_FOR_DYNACONF_* variables"
        )
    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError("Data must be provided")
    client = get_client(obj)
    path = "/".join(
        [obj.VAULT_PATH_FOR_DYNACONF, obj.current_env.lower()]
    ).replace("//", "/")
    client.write(path, data=data)
    load(obj)
