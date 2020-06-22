# Configuring Dynaconf

Dynaconf can be configured through variables suffixed with `_FOR_DYNACONF` those settings can be used to change various dynaconf defaults and behaviors.

Each config variable here can be exported to environment variables or wrote to `.env` file, example:

```bash
export ENV_FOR_DYNACONF=production
```

Or when using your own Dynaconf instance you can pass as parameters directly:

```py
from dynaconf import LazySettings
settings = LazySettings(
    envvar_prefix='MYPROGRAM',
    envvar='MYPROGRAM_SETTINGS',
)
```

It can also be passed as parameters to extensions like `FlaskDynaconf` or set in the `DjangoDynaconf` on settings.py file.

## Configuration options

> NOTE: Append `_FOR_DYNACONF` when exporting these variables.

```eval_rst
.. csv-table::
    :header: "Variable", "Type", "Usage", "default", "example"
    :widths: 15, 15, 50, 30, 50
    :delim: |

    AUTO_CAST | bool | *@casting* like *@int* is parsed. | true | AUTO_CAST_FOR_DYNACONF=false
    COMMENTJSON_ENABLED | bool | Enable comments in json files. | false (req:*pip install commentjson*) | COMMENTJSON_ENABLED_FOR_DYNACONF=true
    CORE_LOADERS | list | A list of enabled core loaders. | [‘YAML’, ‘TOML’, ‘INI’, ‘JSON’, ‘PY’] | CORE_LOADERS_FOR_DYNACONF=’[“YAML”, “JSON”]’ or ‘[]’
    DOTENV_OVERRIDE | bool | *.env* should override the exported envvars. | false | DOTENV_OVERRIDE_FOR_DYNACONF=true
    DOTENV_PATH | str | Defines where to look for *.env* file. | PROJECT_ROOT | DOTENV_PATH_FOR_DYNACONF=”/tmp/.env”
    ENCODING | str | Encoding to read settings files. | utf-8 | ENCODING_FOR_DYNACONF=”cp1252”
    ENV | str | Working environment. | “development” | ENV_FOR_DYNACONF=production
    *FORCE_ENV | str | Force the working environment | None | FORCE_ENV_FOR_DYNACONF=other
    ENV_SWITCHER | str | Variable used to change working env. | ENV_FOR_DYNACONF | ENV_SWITCHER_FOR_DYNACONF=MYPROGRAM_ENV
    ENVLESS_MODE | bool | Ignore env layering and load everything from file. | False | ENVLESS_MODE_FOR_DYNACONF=true
    ENVVAR | str | The envvar which holds the list of settings files. | ‘SETTINGS_FILE_FOR_DYNACONF’ | ENVVAR_FOR_DYNACONF=MYPROGRAM_SETTINGS
    ENVVAR_PREFIX | str | Prefix for exporting parameters as env vars. Example: If your program is called *MYPROGRAM* you may want users to use *MYPROGRAM_FOO=bar* instead of *DYNACONF_FOO=bar* on envvars. | “DYNACONF” | ENVVAR_PREFIX_FOR_DYNACONF=MYPROGRAM (loads MYPROGRAM_VAR) ENVVAR_PREFIX_FOR_DYNACONF=’’ (loads _VAR) ENVVAR_PREFIX_FOR_DYNACONF=false (loads VAR)
    FRESH_VARS | list | A list of vars to be re-loaded on every access. | [] | FRESH_VARS_FOR_DYNACONF=[“HOST”, “PORT”]
    INCLUDES | list | A list of paths or a glob to load can be a toml-like list, or sep by , or ; | [] | INCLUDES_FOR_DYNACONF=”[‘path1.ext’, ‘folder/*’]” INCLUDES_FOR_DYNACONF=”path1.toml;path2.toml” INCLUDES_FOR_DYNACONF=”path1.toml,path2.toml” INCLUDES_FOR_DYNACONF=”single_path.toml” INCLUDES_FOR_DYNACONF=”single_path/glob/.toml”
    INSTANCE **used only by** *$dynaconf** *cli*. | str | Custom instance of LazySettings Must be an importable Python module. | None | INSTANCE_FOR_DYNACONF=myapp.settings
    LOADERS | list | A list of enabled external loaders. |	[‘dynaconf.loaders.env_loader’] | LOADERS_FOR_DYNACONF=’[‘module.mycustomloader’, …]’
    LOWERCASE_READ | bool | If False first level keys cannot be accessed via lower case attrs |	True | LOWERCASE_READ_FOR_DYNACONF=false
    MERGE_ENABLED | bool | A bool to activate the global merge feature | False | MERGE_ENABLED_FOR_DYNACONF=1
    NESTED_SEPARATOR | str | Separator for nested assignment like `export DYNACONF_DATABASES__NAME='foo'` | `__` double underline | NESTED_SEPARATOR_FOR_DYNACONF='___'
    PRELOAD | list | A list of paths or glob to be pre-loaded before main settings file. | [] | PRELOAD_FOR_DYNACONF="['path1.ext', 'folder/*']"
    REDIS_DB | int | Redis DB. | 0 | REDIS_DB_FOR_DYNACONF=1
    REDIS_ENABLED | bool | Redis loader is enabled. | false | REDIS_ENABLED_FOR_DYNACONF=true
    REDIS_HOST | str | Redis server address. | localhost | REDIS_HOST_FOR_DYNACONF=”localhost”
    REDIS_PORT | int | Redis port. | 6379 | REDIS_PORT_FOR_DYNACONF=8899
    ROOT_PATH | str | Directory to look for settings files. This path is the base to search for files defined in *SETTINGS_FILE*. Dynaconf will also search for files in a relative *config/* subfolder if exists. | *None*. If set Dynaconf will look this path first before it starts to search for file in the other locations. see: `<usage.html#the-settings-files>`_ | ROOT_PATH_FOR_DYNACONF=”/my/custom/absolute/path/”
    SECRETS | str | Path to aditional secrets file to be loaded. |	None | SECRETS_FOR_DYNACONF=/var/jenkins/settings_ci.toml
    SETTINGS_FILE | list, str | List of files to load. | List of all supportes files: *settings.{py,toml,yaml,ini,conf,json} .secrets.{py,toml,yaml,ini,conf,json}*. This var name can be replaced by: *ENVVAR_FOR_DYNACONF=MYPROGRAM_SETTINGS* | SETTINGS_FILE_FOR_DYNACONF=”myconfig.toml” SETTINGS_FILE_FOR_DYNACONF=”[‘conf.toml’,’settings.yaml’]” SETTINGS_FILE_FOR_DYNACONF=”conf.toml,settings.yaml” SETTINGS_FILE_FOR_DYNACONF=”conf.toml;settings.yaml” MYPROGRAM_SETTINGS=”conf.toml,settings.yaml”
    SILENT_ERRORS | bool | Loading errors should be silenced. | true | SILENT_ERRORS_FOR_DYNACONF=false
    SKIP_FILES | list | Files to skip/ignore if found on search tree. | [] | SKIP_FILES_FOR_DYNACONF=”[‘/absolute/path/to/file.ext’]”
    VAULT_ALLOW_REDIRECTS | bool | Vault allow redirects. | None | VAULT_ALLOW_REDIRECTS_FOR_DYNACONF=false
    VAULT_CERT | str | Vault cert/pem file path. | None | VAULT_CERT_FOR_DYNACONF=”~/.ssh/key.pem”
    VAULT_ENABLED | bool | Vault server is enabled. | false | VAULT_ENABLED_FOR_DYNACONF=true
    VAULT_HOST | str | Vault host. | localhost | VAULT_HOST_FOR_DYNACONF=”server”
    VAULT_PATH | str | Vault path to the configuration. | None | VAULT_PATH_FOR_DYNACONF=”secret_data”
    VAULT_MOUNT_POINT | str | Vault mount point to the configuration. | secret | VAULT_MOUNT_POINT_FOR_DYNACONF=”kv”
    VAULT_PORT | str | Vault port. | 8200 | VAULT_PORT_FOR_DYNACONF=”2800”
    VAULT_PROXIES | dict | Vault proxies. | None | VAULT_PROXIES_FOR_DYNACONF={http=”http:/localhost:3128/”}
    VAULT_ROLE_ID | str | Vault Role ID. | None | VAULT_ROLE_ID_FOR_DYNACONF=”some-role-id”
    VAULT_SCHEME | str | Vault scheme. | http | VAULT_SCHEME_FOR_DYNACONF=”https”
    VAULT_SECRET_ID | str | Vault Secret ID. | None | VAULT_SECRET_ID_FOR_DYNACONF=”some-secret-id”
    VAULT_TIMEOUT | int | Vault timeout in seconds. | None | VAULT_TIMEOUT_FOR_DYNACONF=60
    VAULT_TOKEN | str | Vault token. | None | VAULT_TOKEN_FOR_DYNACONF=”myroot”
    VAULT_URL | str | Vault URL. | http:// localhost :8200 | VAULT_URL_FOR_DYNACONF=”http://server/8200”
    VAULT_VERIFY | bool | Vault should verify. | None | VAULT_VERIFY_FOR_DYNACONF=true
    YAML_LOADER | str | yaml method name {safe,full,unsafe}_load. | safe_load | YAML_LOADER_FOR_DYNACONF=unsafe_load
```

## Internal use variables

- FORCE_ENV_FOR_DYNACONF:  This variable exists to support the `from_env` method, the crontib extensions and to use for testing.

## Deprecated options

Some configuration options has been deprecated and replaced with a new name, we try to make it without breaking backwards compatibility with old version, but you may receive a warning if use:

- `PROJECT_ROOT` replaced by `ROOT_PATH_FOR_DYNACONF`
- `PROJECT_ROOT_FOR_DYNACONF` replaced by `ROOT_PATH_FOR_DYNACONF`
- `DYNACONF_NAMESPACE` replaced by `ENV_FOR_DYNACONF`
- `NAMESPACE_FOR_DYNACONF` replaced by `ENV_FOR_DYNACONF`
- `BASE_NAMESPACE_FOR_DYNACONF` replaced by `DEFAULT_ENV_FOR_DYNACONF`
- `DYNACONF_SETTINGS_MODULE` replaced by `SETTINGS_FILE_FOR_DYNACONF`
- `DYNACONF_SETTINGS` replaced by `SETTINGS_FILE_FOR_DYNACONF`
- `SETTINGS_MODULE` replaced by `SETTINGS_FILE_FOR_DYNACONF`
- `DYNACONF_SILENT_ERRORS` replaced by `SILENT_ERRORS_FOR_DYNACONF`
- `DYNACONF_ALWAYS_FRESH_VARS` replaced by `FRESH_VARS_FOR_DYNACONF`
- `GLOBAL_ENV_FOR_DYNACONF` replaced by `ENVVAR_PREFIX_FOR_DYNACONF`
- `SETTINGS_MODULE_FOR_DYNACONF` replaced by `SETTINGS_FILE_FOR_DYNACONF`

```eval_rst
.. autoclass:: dynaconf.default_settings
    :show-inheritance:
```
