

## settings instance

Every command (except the init) will require the Instance can be set using `-i` parameter or `export INSTANCE_FOR_DYNACONF`


## The dynaconf CLI

The `$ dynaconf -i config.settings` cli provides some useful commands

> **IMPORTANT** if you are using [Flask Extension](flask.md) the env var `FLASK_APP` must be defined to use the CLI, and if using [Django Extension](django.md) the `DJANGO_SETTINGS_MODULE` must be defined.

### dynaconf --help

```bash
Usage: dynaconf [OPTIONS] COMMAND [ARGS]...

  Dynaconf - Command Line Interface

  Documentation: https://dynaconf.com/

Options:
  --version            Show dynaconf version
  --docs               Open documentation in browser
  --banner             Show awesome banner
  -i, --instance TEXT  Custom instance of LazySettings
  --help               Show this message and exit.

Commands:
  get       Returns the raw value for a settings key.
  init      Inits a dynaconf project.
  inspect   Inspect the loading history of the given settings instance.
  list      Lists user defined settings or all (including internal configs).
  validate  Validates Dynaconf settings based on provided rules.
  write     Writes data to specific source.
```

### dynaconf init

Use init to easily configure your application configuration, once dynaconf is installed go to the root directory of your application and run:

```
$ dynaconf init -v key=value -v foo=bar -s token=1234
```

The above command will create in the current directory

`settings.toml`

```ini
KEY = "value"
FOO = "bar"
```

also `.secrets.toml`

```ini
TOKEN = "1234"
```

as well as `.gitignore` file ignoring the generated `.secrets.toml`

```ini
# Ignore dynaconf secret files
.secrets.*
```

> For sensitive data in production is recommended using [Vault Server](secrets.md)

```bash
Usage: dynaconf init [OPTIONS]

  Inits a dynaconf project.

  By default it creates a settings.toml and a
  .secrets.toml for [default|development|staging|testing|production|global]
  envs.

  The format of the files can be changed passing --format=yaml|json|ini|py.

  This command must run on the project's root folder or you must pass
  --path=/myproject/root/folder.

  The --env/-e is deprecated (kept for compatibility but unused)

Options:
  -f, --format [ini|toml|yaml|json|py|env]
  -p, --path TEXT                 defaults to current directory
  -e, --env TEXT                  Sets the working env in `.env` file
  -v, --vars TEXT                 extra values to write to settings file e.g:
                                  `dynaconf init -v NAME=foo -v X=2

  -s, --secrets TEXT              secret key values to be written in .secrets
                                  e.g: `dynaconf init -s TOKEN=kdslmflds

  --wg / --no-wg
  -y
  --django TEXT
  --help                          Show this message and exit.
```

Note that `-i`/`--instance` cannot be used with `init` as `-i` must point to an existing instance of the settings.


### Dynaconf inspect (tech preview)

> **NEW in 3.2.0**

!!! warning
    This feature is in **tech preview** the usage interface and output format is
    subject to change.

Inspect and dump data's loading history about a specific key or environment.

It is also available as a [utility function](advanced.md#inspecting-history).

```
Usage: dynaconf inspect [OPTIONS]

  Inspect the loading history of the given settings instance.

  Filters by key and environment, otherwise shows all.

Options:
  -k, --key TEXT                  Filters result by key.
  -e, --env TEXT                  Filters result by environment on --report-
                                  mode=inspect.

  -f, --format [yaml|json|json-compact]
                                  The output format.
  -s, --old-first                 Invert history sorting to 'old-first' on
                                  --report-mode=inspect.

  -n, --limit INTEGER             Limits how many history entries are shown on
                                  --report-mode=inspect.

  -a, --all                       Show dynaconf internal settings?
  -m, --report-mode [inspect|debug]
  -v, --verbose                   Increase verbosity of the output on
                                  --report-mode=debug.

  --help                          Show this message and exit.
                    Show this message and exit.
```

Sample usage:

```yaml
>>> dynaconf -i app.settings inspect -k foo -f yaml -n 2
header:
  env_filter: 'foo'
  key_filter: None
  new_first: 'True'
  history_limit: None
  include_internal: 'False'
current: from_environ
history:
- loader: yaml
  identifier: file_a.yaml
  env: default
  merged: false
  value:
    FOO: from_yaml
- loader: env_global
  identifier: unique
  env: global
  merged: false
  value:
    FOO: from_environ
    BAR: environ_only
```

To save to a file, use regular stream redirect methods:

```bash
$ dynaconf -i app.settings inspect -k foo -f yaml > dump.yaml
```

#### Inspect Debug Info

> **NEW** in version 3.2.8

Prints debug information about the current settings instance

```bash
dynaconf inspect -m debug -vv
```

Verbosity levels are

- 0 (default): Include only the count of keys loaded by each loader
- 1: Include the keys loaded by each loader
- 2: Include the keys loaded by each loader and the values of each key


Debug mode also accepts the `-k key` to filter the output by a specific key.


Sample output in YAML format:

**TIP**: adding `-v` will list the keys and `-vv` will list the keys and values. 

```yaml
# dynaconf inspect -m debug --format=yaml
versions:
  dynaconf: 3.2.8
  django: 4.2.16
root_path: /app/settings
validators: ["Validator("FOO", must_exist=True, eq="bar")"]
core_loaders: ["dynaconf.loaders.env_loader"]
loaded_files:
- /app/settings/defaults.py
- /app/settings/development_defaults.py
- /etc/app/settings.yaml
history:
- loader: set_method
  identifier: init_kwargs
  data: 13
- loader: set_method
  identifier: default_settings
  data: 56
- loader: settings_loader
  identifier: /app/settings/defaults
  data: 256
- loader: py
  identifier: /app/settings/development_defaults
  data: 16
- loader: set_method
  identifier: lambda_1933577857047901425@instance
  data: 2
- loader: standard_settings_loader
  identifier: /etc/app/settings.yaml
  data: 1
post_hooks:
- <function <lambda> at 0x716a7b89c900>
loaded_hooks:
- hook: lambda_1933577857047901425@instance
  data: 1
environments:
- development
- production
loaded_envs: ['development']
```

### Dynaconf get

Get raw value for a single key

```bash
Usage: dynaconf get [OPTIONS] KEY

  Returns the raw value for a settings key.

  If result is a dict, list or tuple it is printed as a valid json string.

Options:
  -d, --default TEXT  Default value if settings doesn't exist
  -e, --env TEXT      Filters the env to get the values
  -u, --unparse       Unparse data by adding markers such as @none, @int etc..
  --help              Show this message and exit.
```

Example:

```bash
export FOO=$(dynaconf get DATABASE_NAME -d 'default')
```

If the key doesn't exist and no default is provided it will exit with code 1.

### dynaconf list

List all defined parameters and optionally export to a json file.

```
Usage: dynaconf list [OPTIONS]

  Lists user defined settings or all (including internal configs).

  By default, shows only user defined. If `--all` is passed it also shows
  dynaconf internal variables aswell.

Options:
  -e, --env TEXT     Filters the env to get the values
  -k, --key TEXT     Filters a single key
  -m, --more         Pagination more|less style
  -l, --loader TEXT  a loader identifier to filter e.g: toml|yaml
  -a, --all          show dynaconf internal settings?
  -o, --output FILE  Filepath to write the listed values as json
  -j, --json         Prints out a valid JSON string
  --output-flat      Output file is flat (do not include [env] name)
  --help             Show this message and exit.
```

#### Printing out the settings as JSON

```console
$ dynaconf list --json
{"a_valid_raw": "json_output"}
```

The above output is printed to stdout and can be piped to a file or processed
using tools such as `jq`.

#### Exporting current environment as a file

```bash
dynaconf list -o path/to/file.yaml
```

The above command will export all the items showed by `dynaconf list` to the desired format which is inferred by the `-o` file extension, supported formats `yaml, toml, ini, json, py`

When using `py` you may want a flat output (without being nested inside the env key)

```bash
dynaconf list -o path/to/file.py --output-flat
```

### dynaconf write

```
Usage: dynaconf write [OPTIONS] [ini|toml|yaml|json|py|redis|vault|env]

  Writes data to specific source

Options:
  -v, --vars TEXT     key values to be written e.g: `dynaconf write toml -e
                      NAME=foo -e X=2

  -s, --secrets TEXT  secret key values to be written in .secrets e.g:
                      `dynaconf write toml -s TOKEN=kdslmflds -s X=2

  -p, --path TEXT     defaults to current directory/settings.{ext}
  -e, --env TEXT      env to write to defaults to DEVELOPMENT for files for
                      external sources like Redis and Vault it will be
                      DYNACONF or the value set in $ENVVAR_PREFIX_FOR_DYNACONF

  -y
  --help              Show this message and exit.
```

### dynaconf validate

> **NEW in 1.0.1**

Starting on version 1.0.1 it is possible to define validators in **TOML** file called **dynaconf_validators.toml** placed in the same folder as your settings files.

`dynaconf_validators.toml` equivalent to program above

```ini
[default]

version = {must_exist=true}
name = {must_exist=true}
password = {must_exist=false}

  [default.age]
  must_exist = true
  lte = 30
  gte = 10

[production]
project = {eq="hello_world"}
```

Then to fire the validation use:

```
$ dynaconf -i config.settings validate
```

If validates it returns status 0 (success) and this command can be called in your CI/CD/Deploy jobs.

### dynaconf --version

returns dynaconf version

```
$ dynaconf -i config.settings --version
1.0.0
```

### dynaconf --docs

Opens Dynaconf documentation in browser


### dynaconf --banner

Prints this awesome ascii made banner in the console :)

```
$ dynaconf -i config.settings --banner

██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝

Learn more at: http://github.com/dynaconf/dynaconf
```
