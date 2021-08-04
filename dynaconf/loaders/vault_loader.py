# docker run -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
# pip install hvac
from dynaconf.utils import build_env_list
from dynaconf.utils.parse_conf import parse_conf_data

try:
    import boto3
except ImportError:
    boto3 = None

try:
    from hvac import Client
    from hvac.exceptions import InvalidPath
except ImportError:
    raise ImportError(
        "vault package is not installed in your environment. "
        "`pip install dynaconf[vault]` or disable the vault loader with "
        "export VAULT_ENABLED_FOR_DYNACONF=false"
    )


IDENTIFIER = "vault"


# backwards compatibility
_get_env_list = build_env_list


def get_client(obj):
    client = Client(
        **{k: v for k, v in obj.VAULT_FOR_DYNACONF.items() if v is not None}
    )
    if obj.VAULT_ROLE_ID_FOR_DYNACONF is not None:
        client.auth_approle(
            role_id=obj.VAULT_ROLE_ID_FOR_DYNACONF,
            secret_id=obj.get("VAULT_SECRET_ID_FOR_DYNACONF"),
        )
    elif obj.VAULT_ROOT_TOKEN_FOR_DYNACONF is not None:
        client.token = obj.VAULT_ROOT_TOKEN_FOR_DYNACONF
    elif obj.VAULT_AUTH_WITH_IAM_FOR_DYNACONF:
        if boto3 is None:
            raise ImportError(
                "boto3 package is not installed in your environment. "
                "`pip install boto3` or disable the VAULT_AUTH_WITH_IAM"
            )

        session = boto3.Session()
        credentials = session.get_credentials()
        client.auth.aws.iam_login(
            credentials.access_key,
            credentials.secret_key,
            credentials.token,
            role=obj.VAULT_AUTH_ROLE_FOR_DYNACONF,
        )
    assert client.is_authenticated(), (
        "Vault authentication error: is VAULT_TOKEN_FOR_DYNACONF or "
        "VAULT_ROLE_ID_FOR_DYNACONF defined?"
    )
    client.kv.default_kv_version = obj.VAULT_KV_VERSION_FOR_DYNACONF
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
    try:
        dirs = client.secrets.kv.list_secrets(
            path=obj.VAULT_PATH_FOR_DYNACONF,
            mount_point=obj.VAULT_MOUNT_POINT_FOR_DYNACONF,
        )["data"]["keys"]
    except InvalidPath:
        # The given path is not a directory
        dirs = []
    env_list = dirs + build_env_list(obj, env)
    for env in env_list:
        path = "/".join([obj.VAULT_PATH_FOR_DYNACONF, env])
        try:
            if obj.VAULT_KV_VERSION_FOR_DYNACONF == 2:
                data = client.secrets.kv.v2.read_secret_version(
                    path, mount_point=obj.VAULT_MOUNT_POINT_FOR_DYNACONF
                )
            else:
                data = client.secrets.kv.read_secret(
                    "data/" + path,
                    mount_point=obj.VAULT_MOUNT_POINT_FOR_DYNACONF,
                )
        except InvalidPath:
            # If the path doesn't exist, ignore it and set data to None
            data = None
        if data:
            # There seems to be a data dict within a data dict,
            # extract the inner data
            data = data.get("data", {}).get("data", {})
        try:
            if obj.VAULT_KV_VERSION_FOR_DYNACONF == 2 and data:
                data = data.get("data", {})
            if data and key:
                value = parse_conf_data(
                    data.get(key), tomlfy=True, box_settings=obj
                )
                if value:
                    obj.set(key, value)
            elif data:
                obj.update(data, loader_identifier=IDENTIFIER, tomlfy=True)
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
    data = {"data": data}
    client = get_client(obj)
    if obj.VAULT_KV_VERSION_FOR_DYNACONF == 1:
        mount_point = obj.VAULT_MOUNT_POINT_FOR_DYNACONF + "/data"
    else:
        mount_point = obj.VAULT_MOUNT_POINT_FOR_DYNACONF
    path = "/".join([obj.VAULT_PATH_FOR_DYNACONF, obj.current_env.lower()])
    client.secrets.kv.create_or_update_secret(
        path, secret=data, mount_point=mount_point
    )
    load(obj)


def list_envs(obj, path=""):
    """
    This function is a helper to get a list of all the existing envs in
    the source of data, the use case is:
        existing_envs = vault_loader.list_envs(settings)
        for env in exiting_envs:
            with settings.using_env(env):  # switch to the env
            # do something with a key of that env

    :param obj: settings object
    :param path: path to the vault secrets
    :return: list containing all the keys at the given path
    """
    client = get_client(obj)
    path = path or obj.get("VAULT_PATH_FOR_DYNACONF")
    try:
        return client.list(f"/secret/metadata/{path}")["data"]["keys"]
    except TypeError:
        return []
