# Getting Started

## Installation

> Python 3.x is required

```
$ pip install dynaconf
```

> Default installation supports .toml, .py and .json file formats and also environment variables (.env supported) - to support YAML add `pip install dynaconf[yaml]` or `pip install dynaconf[all]`

## Usage

### Accessing config variables in your Python application

In your Python program wherever you need to access a settings variable you use the canonical object `from dynaconf import settings`:

#### Example of program to connect to some database

```python
from some.db import Client

from dynaconf import settings

conn = Client(
    username=settings.USERNAME,             # attribute style access
    password=settings.get('PASSWORD'),      # dict get style access
    port=settings['PORT'],                  # dict item style access
    timeout=settings.as_int('TIMEOUT'),     # Forcing casting if needed
    host=settings.get('HOST', 'localhost')  # Providing defaults
)
```

### Understanding the settings

Dynaconf aims to have a flexible and usable configuration system. Your applications can be configured via a [**configuration files**](#the-settings-files), through [**environment variables**](environment_variables.html), or both. Configurations can be separated into environments: **[default], [development], [staging], [testing] and [production]**. The working environment is switched via an environment variable.

But this is all **optional** you can of course follow strictly the [12 factor app](https://12factor.net/config) guide, have your configuration coming only from environment variables and provide files only to store `[default]` values. (take also a look on how to add a [dynaconf validation](validation.html) file to your project).

**Sensitive data** like tokens, secret keys and password can be stored in `.secrets.*` files and/or [external storages](external_storages.html) like `Redis` or `vault` secrets server.

Besides the built-in optional support to **Redis** as settings storage dynaconf allows you to create [**Custom Loaders**](extend.html) and store the data wherever you want e.g: databases, memory storages, other file formats, nosql databases etc.

## Working environments

At any point in time, your application is operating in a given configuration environment. By default there are four such environments:

- [development] (selected by default)
- [staging]
- [testing]
- [production]
- [{custom}] <-- You can create named environments that you need

> There is also the pseudo-envs **[default]** to provide comprehensive default values and **[global]** to provide global values to override in any other environment.

Without any action, your applications by default run in the **[development]** environment. The environment can be changed via the `ENV_FOR_DYNACONF` environment variable. For example, to launch an application in the **[staging]** environment, we can run:

```bash
export ENV_FOR_DYNACONF=staging
```

or

```bash
ENV_FOR_DYNACONF=staging python yourapp.py
```

> **NOTE:** When using [Flask Extension](flask.html) the environment can be changed via `FLASK_ENV` variable and for [Django Extension](django.html) you can use `DJANGO_ENV`.

## Disabling Working environments

In some cases you might want to disable the layered environment separation and just load everything from a file use:

```bash
export ENVLESS_MODE_FOR_DYNACONF=true
```

or pass this setting to your own Dynaconf instance

```py
from dynaconf import LazySettings

settings = LazySettings(ENVLESS_MODE=True)
```

## The settings files

> **NOTE:** The settings files are optional. If it is not present, only the values from **environment variables** and enabled external loaders are used (**.env** file is also supported).

Dynaconf will search for the settings files defined in `SETTINGS_FILE_FOR_DYNACONF` which by default is a list containing combinations of **settings.{py|toml|json|ini|yaml}** and **.secrets.{py|toml|json|ini|yaml}**
and dynaconf will try to find each one of those combinations, optionally it is possible to configure it to a different set of files e.g: `export SETTINGS_FILE_FOR_DYNACONF='["myfilename.toml", "another.json"]'`, this value contains a list of relative or absolute paths, can be a toml-like list or a comma/semicolon separated string and can be exported to `envvars`, write to `.env` file or passed directly to Dynaconf instance.

> IMPORTANT: Dynaconf by default reads settings files using `utf-8` encoding, if you have settings files written in other encoding please set `ENCODING_FOR_DYNACONF` environment variable.

See more details in [configuration](configuration.html)

## Settings files location

To find the files defined in `SETTINGS_FILE_FOR_DYNACONF` the search will start at the path defined in `ROOT_PATH_FOR_DYNACONF` (if defined), then will recursively walk to its root and then will try the **folder where the called program is located** and then it will recursively try its parent directories **until the root parent is reached which can be File System `/` or the current working dir** then finally will try the **current working directory** as the last option.

> **NOTE**: If by any reason you need Dynaconf to first look at the current working dir you can customize the `ROOT_PATH_FOR_DYNACONF` via environment variable or by creating a [custom settings object](advanced_usage.html#customizing-the-settings-object)

Some people prefer to put settings in a sub-folder so for each of the paths it will also search in a relative folder called `config/`.

And for each file dynaconf will also try to load a `.local.` file, for example, if you have a `settings.toml` after loading it Dynaconf will also try to find a `settings.local.toml` if exists.

Dynaconf will stop searching on the first match for each file and if no file is found it will **fail silently** unless `SILENT_ERRORS_FOR_DYNACONF=false` is exported.

### Illustrative Example

> **New in 2.0.0**

If your program has the following structure:

```text
|_ myprogram/
   |_ src/
      |_ app.py
         # from dynaconf import settings
         # print(settings.NAME)
         # print(settings.PASSWORD)
         # print(settings.FOO)
   |_ config
      |_ settings.toml
         # [default]
         # name = "Jon Doe"
   |_ settings.local.toml
      # [default]
      # name = "Oscar Wilde"
   |_ .env
      # DYNACONF_FOO='BAR'
   |_ .secrets.toml
      # [default]
      # password = "Utopi@"
```

And you call it from `myprogram` working dir.

```bash
cd myprogram
python src/app.py
```

What happens is:

> NOTE: The behavior explained here is valid only for the above file structure, other arrangements are possible and depending on how folders are organized dynaconf can behave differently.

1. app.py:1 does `from dynaconf import settings`

    -  Only the `.env` file will be searched, other settings are lazy evaluated.
    -  `.env` will be searched starting on `myprogram/src/.env`
    -  if not found then `myprogram/src/config/.env` 
    -  if not found then `myprogram/.env`  **actually found here so stops searching**
    -  if not found then `myprogram/config/.env`
    -  It will load all values from `.env` to the environment variables and create the instance of `settings`

2. app.py:2 does the first access to a settings on `print(settings.NAME)`

    - Dynaconf will execute the loaders defined in `CORE_LOADERS` and `LOADERS`, it will initialize the `settings` object and start the file search.
    - `settings.{py|toml|json|ini|yaml}` will be searched on `myprogram/src/`
    - if not found then `myprogram/src/config`
    - if not found then `myprogram/`
    - if not found then `myprogram/config` **settings.toml actually found here so stops searching for toml**
    - It will load all the values defined in the `settings.toml`
    - It will continue to look all the other files e.g: settings.json, settings.ini, settings.yaml etc.
    - Then
    - It will search for **.secrets.{py|toml|json|ini|yaml}** on `myprogram/src/`
    - if not found then `myprogram/src/config`
    - if not found then `myprogram/`  **.secrets.toml actually found here so stops searching for toml**
    - if not found then `myprogram/config` 
    - It will load all the values defined in `.secrets.toml` (if filename is `*.secret.*` values are hidden on logs)
    - It will continue to look all the other files e.g: .secrets.json, .secrets.ini, .secrets.yaml etc.
    - Then
    - It will iterate the list of loaded files containing `[settings.toml, .secrets.toml]` and for each of them it will also try to find a `settings.local.toml` (**found in myprogram/settings.local.toml**) and a `.secrets.local.toml` using the same search tree until it is found or it will skip if not found.
    - Then
    - It will execute **external loaders** like `Redis` and `Vault` if enabled.
    - It will execute **custom loaders** if configured.
    - Then finally
    - It will read all **environment variables** prefixed with `DYNACONF_` and load its values, in our example it loads `FOO='BAR'` from `.env` file.

3. app.py:3 does second access to a settings on `print(settings.PASSWORD)` 

    - All the loaders, loaded files, config options and vars are now **cached** no loading has been executed.
    - Only if `settings.get_fresh('PASSWORD')` is used, dynaconf will force a re-load of everything to ensure the fresh value.
    - Also if `settings.using_env|from_env` or `ENV_FOR_DYNACONF` switched, e.g: from `[development]` to `[staging]`, then re-load happens.
    - It is also possible to explicitly force a `load` or `reload`.

4. Complete program output is:

```bash
Oscar Wilde
Utopi@
BAR
```

## Loading order

Dynaconf loads file in a overriding cascade loading order using the predefined order:

1. First the environment variables (and `.env` file) to read for [configuration](configuration.html) options
2. Then the paths provided in `PRELOAD_FOR_DYNACONF` using all enabled loaders.
3. Then the files defined in `SETTINGS_FILE_FOR_DYNACONF` using all enabled loaders.
    - Files containing `.local.` in its name will be loaded at the end. e.g: `settings.local.yaml`
4. Then contents of `SECRETS_FOR_DYNACONF` envvar filename if defined (useful for jenkins and other CI)
5. Then the loaders defined in `LOADERS_FOR_DYNACONF` 
    - Redis if enabled by `REDIS_FOR_DYNACONF=1`
    - Vault if enabled by `Vault_FOR_DYNACONF=1`
    - Custom loaders if any added
    - Environment variables loader will be the last always
6. If there is any `DYNACONF_INCLUDE` key found or `INCLUDES_FOR_DYNACONF` env vars this will be loaded.

The order can be changed by overriding the `SETTINGS_FILE_FOR_DYNACONF` the `CORE_LOADERS_FOR_DYNACONF` and `LOADERS_FOR_DYNACONF` variables.

> **NOTE**: Dynaconf works in an **layered override** mode based on the above order, so if you have multiple file formats with conflicting keys defined, the precedence will be based on the loading order.
> If you dont want to have values like `lists` and `dicts` overwritten take a look on how to [merge existing values](usage.html#merging-existing-values)

## Local configuration files and merging to existing data

> New in **2.2.0**

This feature is useful for maintaining a shared set of config files for a team, while still allowing for local configuration.

Any file matched by the glob `*.local.*` will be read at the end of file loading order. So it is possible to have local settings files that are for example not committed to the version controlled repository. (e:g add `**/*.local*` to your `.gitignore`)

So if you have `settings.toml` Dynaconf will load it and after all will also try to load a file named `settings.local.toml` if it does exist. And the same applies to all the other supported extensions `settings.local.{py,json,yaml,toml,ini,cfg}`

Example:

```ini
# settings.toml        # <-- 1st loaded
[default]
colors = ["green", "blue"]
parameters = {enabled=true, number=42}

# .secrets.toml        # <-- 2nd loaded  (overrides previous existing vars)
[default]
password = 1234

# settings.local.toml  # <-- 3rd loaded  (overrides previous existing vars)
[default]
colors = ["pink"]
parameters = {enabled=false}
password = 9999
```

So with above the values will be:

```python
settings.COLORS == ["pink"]
settings.PARAMETERS == {"enabled": False}
settings.PASSWORD == 9999
```

For each loaded file dynaconf will `override` previous existing keys so if you want to `append` new values to existing variables you can use 3 strategies.

### Mark the local file to be entirely merged

> New in **2.2.0**

```ini
# settings.local.toml
dynaconf_merge = true
[default]
colors = ["pink"]
parameters = {enabled=false}
```

By adding `dynaconf_merge` to the top root of the file mark entire file to be merged.

And then the values will be updated in to existing data structures.

```python
settings.COLORS == ["pink", "green", "blue"]
settings.PARAMETERS == {"enabled": False, "number": 42}
settings.PASSWORD == 9999
```

You can also mark a single `env` like `[development]` to be merged.

```ini
# settings.local.toml
[development]
dynaconf_merge = true
colors = ["pink"]
parameters = {enabled=false}
```

### dynaconf merge token

```ini
# settings.local.toml
[default]
colors = ["pink", "dynaconf_merge"]
parameters = {enabled=false, dynaconf_merge=true}
```

By adding `dynaconf_merge` to a `list` or `dict` marks it as a merge candidate.

And then the values will be updated in to existing data structures.

```python
settings.COLORS == ["pink", "green", "blue"]
settings.PARAMETERS == {"enabled": False, "number": 42}
settings.PASSWORD == 9999
```

> New in **2.2.0**

And it also works having `dynaconf_merge` as dict keys holding the value to be merged.

```ini
# settings.local.toml
[default.colors]
dynaconf_merge = ["pink"]  # <-- value ["pink"] will be merged in to existing colors

[default.parameters]
dynaconf_merge = {enabled=false}
```

### Dunder merging for nested structures

For nested structures the recommendation is to use dunder merging because it it easier to read and also it has no limitations in terms of nesting levels.

```ini
# settings.local.yaml
[default]
parameters__enabled = false
```

The use of `__` to denote nested level will ensure the key is merged with existing values read more in [merging existing values](#merging-existing-values).

### Global merge

```bash
export MERGE_ENABLED_FOR_DYNACONF=true
```

or put it in your `.env` file then Dynaconf will automatically merge all existing variables.

> **BEWARE**: Using `MERGE_ENABLED_FOR_DYNACONF` can lead to unexpected results because you do not have granular control of what is being merged or overwritten so the recommendation is to use other options.

## Settings File Formats

The recommended file format is **TOML** but you can choose to use any of **.{py|toml|json|ini|yaml}**.

The file must be a series of sections, at least one for **[default]**, optionally one for each **[environment]**, and an optional **[global]** section. Each section contains **key-value** pairs corresponding to configuration parameters for that **[environment]**. If a configuration parameter is missing, the value from **[default]** is used. The following is a complete `settings.toml` file, where every standard configuration parameter is specified within the **[default]** section:

> **NOTE**: if the file format choosen is `.py` as it does not support sections you can create multiple files like `settings.py` for [default], `development_settings.py`, `production_settings.py` and `global_settings.py`. **ATTENTION**: using `.py` is not recommended for configuration - prefer to use static files like **TOML**!

```ini
[default]
username = "admin"
port = 5000
host = "localhost"
message = "default message"
value = "default value"

[development]
username = "devuser"

[staging]
host = "staging.server.com"

[testing]
host = "testing.server.com"

[production]
host = "server.com"

[awesomeenv]
value = "this value is set for custom [awesomeenv]"

[global]
message = "This value overrides message of default and other envs"
```

The **[global]** pseudo-environment can be used to set and/or override configuration parameters globally. A parameter defined in a **[global]** section sets, or overrides if already present, that parameter in every environment. 

> IMPORTANT: the environments and pseudo envs such as `[global], ['default']` affects only the current file, it means that a value in `[global]` will override values defined only on that file or previous loaded files, if in another file the value is reloaded then the global values is overwritten. Dynaconf supports multiple file formats but the recommendation is not to mix them, choose a format and stick with it.

For example, given the following `settings.toml` file, the value of address will be **"1.2.3.4"** in every environment:

```cfg
[global]
address = "1.2.3.4"

[development]
address = "localhost"

[production]
address = "0.0.0.0"
```

> **NOTE**: The **[env]** name and first level variables are case insensitive as internally dynaconf will always use upper case, that means **[development]** and **[DEVELOPMENT]** are equivalent and **address** and **ADDRESS** are also equivalent. **But the recommendation is to `always use lower case in files` and `always use upper case in env vars and .py files`** (This rule does not apply for inner data structures as dictionaries and arrays).

## Supported file formats

By default **toml** is the recommended format to store your configuration, however you can switch to a different supported format.

```bash
# If you wish to include support for more sources
pip3 install dynaconf[yaml|ini|redis|vault]

# for a complete installation
pip3 install dynaconf[all]
```

Once the support is installed no extra configuration is needed to load data from those files.

If you need a different file format take a look on how to extend dynaconf writing a [custom loader](extend.html)

## Additional secrets file (for CI, jenkins etc.)

It is common to have an extra `secrets` file that is available only when running on specific CI environment like `Jenkins`, usually there will be an environment variable pointing to the file.

On Jenkins it is done on job settings by exporting the `secrets` information.

Dynaconf can handle this via `SECRETS_FOR_DYNACONF` environment variable.

ex:

```bash
export SECRETS_FOR_DYNACONF=/path/to/settings.toml{json|py|ini|yaml}
```

If that variable exists in your environment then Dynaconf will also load it.

## Including files inside files

Sometimes you have multiple fragments of settings in different files, dynaconf allow easy merging of those files via `dynaconf_include`.

Example:

`plugin1.toml`

```cfg
[development]
plugin_specific_variable = 'value for development'
```

and even mixing different formats:  
`plugin2.yaml`

```yaml
production:
  plugin_specific_variable: 'value for production'
```

Then it can be merged on main `settings.toml` file via `dynaconf_include`

`settings.toml`

```cfg
[default]
dynaconf_include = ["plugin1.toml", "plugin2.yaml"]
DEBUG = false
SERVER = "base.example.com"
PORT = 6666
```

A settings file can include a `dynaconf_include` stanza, whose exact
  syntax will depend on the type of settings file (json, yaml, toml, etc)
  being used:

  ```cfg
  [default]
  dynaconf_include = ["/absolute/path/to/plugin1.toml", "relative/path/to/plugin2.toml"]
  DEBUG = false
  SERVER = "www.example.com"
  ```

  When loaded, the files located at the (relative or absolute) paths in
  the `dynaconf_include` key will be parsed, in order, and override any
  base settings that may exist in your current configuration.

  The paths can be relative to the base `settings.(toml|yaml|json|ini|py)`
  file, or can be absolute paths.

  The idea here is that plugins or extensions for whatever framework or
  architecture you are using can provide their own configuration values
  when necessary.

  It is also possible to specify glob-based patterns:

  ```cfg
  [default]
  dynaconf_include = ["configurations/*.toml"]
  DEBUG = false
  SERVER = "www.example.com"
  ```

  Currently, only a single level of includes is permitted to keep things
  simple and straightforward.

### Including via environment variable

It is also possible to setup includes using environment variable.

```bash
# A glob pattern
export INCLUDES_FOR_DYNACONF='/etc/myprogram/conf.d/*.toml'
# a single path
export INCLUDES_FOR_DYNACONF='/path/to/file.yaml'
# multiple files
export INCLUDES_FOR_DYNACONF='/path/to/file.yaml;/other/path/to/file.toml'
```

## Programmatically loading a settings file

```python
from dynaconf import settings
settings.load_file(path="/path/to/file.toml")  # list or `;/,` separated allowed
```

> **NOTE**: programmatically loaded file is not persisted, once `env` is changed via `setenv|ugin_env`, or a `reload` or `configure` is invoked it will be cleaned, to persist it needs to go to `INCLUDES_FOR_DYNACONF` variable or you need to load it programmatically again.

## Template substitutions

Dynaconf has 2 tokens to enable string substitutions `@format` and `@jinja`.

### @format token

Dynaconf allows template substitutions for strings values, by using the `@format` token prefix and including placeholders accepted by Python's `str.format` method Dynaconf will call
it lazily upon access time.

The call will be like:

```py
"<YOURVALUE>".format(env=os.environ, this=dynaconf.settings)
```

So in your string you can refer to environment variables via `env` object, and also to variables defined int the settings object itself via `this` reference. It is lazily evaluated on access it will use the final value for a settings regardless the order of load.

Example:

```bash
export PROGRAM_NAME=calculator
```

settings.toml

```toml
[default]
DB_NAME = "mydb.db"

[development]
DB_PATH = "@format {env[HOME]}/{this.current_env}/{env[PROGRAM_NAME]}/{this.DB_NAME}"
```

- `{env[HOME]}` is the same as `os.environ["HOME"]` or `$HOME` in the shell.
- `{this.current_env}` is the same as `settings.current_env`
- `{env[PROGRAM_NAME]}` is the same as `os.environ["PROGRAM_NAME"]` or `$PROGRAM_NAME` in the shell.
- `{this.DB_NAME}` is the same as `settins.DB_NAME` or `settings["DB_NAME"]`

so in your `program`

```py
from dynaconf import settings

settings.DB_PATH == '~/DEVELOPMENT/calculator/mydb.db'
```

### @jinja token

If `jinja2` package is installed then dynaconf will also allow the use jinja to render string values.

Example:

```bash
export PROGRAM_NAME=calculator
```

settings.toml

```toml
[default]
DB_NAME = "mydb.db"

[development]
DB_PATH = "@jinja {{env.HOME}}/{{this.current_env | lower}}/{{env['PROGRAM_NAME']}}/{{this.DB_NAME}}"
```

so in your `program`

```py
from dynaconf import settings

settings.DB_PATH == '~/development/calculator/mydb.db'
```

The main difference is that Jinja allows some Python expressions to be avaluated such as `{% for, if, while %}` and also supports calling methods and has lots of filters like `| lower`.

Jinja supports its built-in filters listed in [Builtin Filters Page](http://jinja.palletsprojects.com/en/master/templates/#builtin-filters) and Dynaconf includes aditional filters for `os.path` module: `abspath`. `realpath`, `relpath`, `basename` and `dirname` and usage is like: `VALUE = "@jinja {{this.FOO | abspath}}"`

## Merging existing data structures

If your settings has existing variables of types `list` ot `dict` and you want to `merge` instead of `override` then 
the `dynaconf_merge` and `dynaconf_merge_unique` stanzas can mark that variable as a candidate for merging.

For **dict** value:

Your main settings file (e.g `settings.toml`) has an existing `DATABASE` dict setting on `[default]` env.

Now you want to contribute to the same `DATABASE` key by adding new keys, so you can use `dynaconf_merge` at the end of your dict:

In specific `[envs]`

```cfg
[default]
database = {host="server.com", user="default"}

[development]
database = {user="dev_user", dynaconf_merge=true}

[production]
database = {user="prod_user", dynaconf_merge=true}
```

also allowed the alternative short format

```cfg
[default]
database = {host="server.com", user="default"}

[development.database]
dynaconf_merge = {user="dev_user"}

[production.database]
dynaconf_merge = {user="prod_user"}
```

In an environment variable:

Using `@merge` mark

```bash
# Toml formatted envvar
export DYNACONF_DATABASE='@merge {password=1234}'
```

or `@merge` mark short format

```bash
# Toml formatted envvar
export DYNACONF_DATABASE='@merge password=1234'
```

It is also possible to use nested `dunder` traversal like:

```bash
export DYNACONF_DATABASE__password=1234
export DYNACONF_DATABASE__user=admin
export DYNACONF_DATABASE__ARGS__timeout=30
export DYNACONF_DATABASE__ARGS__retries=5
```

Each `__` is parsed as a level traversing thought dict keys. read more in [environment variables](environment_variables.html#nested-keys-in-dictionaries-via-environment-variables)

So the above will result in

```py
DATABASE = {'password': 1234, 'user': 'admin', 'ARGS': {'timeout': 30, 'retries': 5}}
```

> **IMPORTANT** lower case keys are respected only on *nix systems, unfortunately Windows environment variables are case insensitive and Python reads it as all upper cases, that means that if you are running on Windows the dictionary can have only upper case keys.

You can also export a toml dictionary.

```bash
# Toml formatted envvar
export DYNACONF_DATABASE='{password=1234, dynaconf_merge=true}'
```

Or in an additional file (e.g `settings.yaml, .secrets.yaml, etc`) by using `dynaconf_merge` token:

```yaml
default:
  database:
    password: 1234
    dynaconf_merge: true
```

or

```yaml
default:
  database:
    dynaconf_merge:
      password: 1234
```

The `dynaconf_merge` token will mark that object to be merged with existing values (of course `dynaconf_merge` key will not be added to the final settings it is just a mark)

The end result will be on `[development]` env:

```python
settings.DATABASE == {'host': 'server.com', 'user': 'dev_user', 'password': 1234}
```

The same can be applied to **lists**:

`settings.toml`

```cfg
[default]
plugins = ["core"]

[development]
plugins = ["debug_toolbar", "dynaconf_merge"]
```

or

```cfg
[default]
plugins = ["core"]

[development.plugins]
dynaconf_merge = ["debug_toolbar"]
```

And in environment variable

using `@merge` token

```bash
export DYNACONF_PLUGINS='@merge ["ci_plugin"]'
```

or short version

```bash
export DYNACONF_PLUGINS='@merge ci_plugin'
```

comma separated values also supported:

```bash
export DYNACONF_PLUGINS='@merge ci_plugin,other_plugin'
```

or explicitly

```bash
export DYNACONF_PLUGINS='["ci_plugin", "dynaconf_merge"]'
```

Then the end result on `[development]` is:

```python
settings.PLUGINS == ["ci_plugin", "debug_toolbar", "core"]
```

If your value is a dictionary:

```bash
export DYNACONF_DATA="@merge {foo='bar'}"

# or the short

export DYNACONF_DATA="@merge foo=bar"
```

### Avoiding duplications on lists

The `dynaconf_merge_unique` is the token for when you want to avoid duplications in a list.

Example:

```cfg
[default]
scripts = ['install.sh', 'deploy.sh']

[development]
scripts = ['dev.sh', 'test.sh', 'deploy.sh', 'dynaconf_merge_unique']
```

```bash
export DYNACONF_SCRIPTS='["deploy.sh", "run.sh", "dynaconf_merge_unique"]'
```

The end result for `[development]` will be:

```python
settings.SCRIPTS == ['install.sh', 'dev.sh', 'test.sh', 'deploy.sh', 'run.sh']
```

> Note that `deploy.sh` is set 3 times but it is not repeated in the final settings.

### Known caveats

The **dynaconf_merge** and **@merge** functionalities works only for the first level keys, it will not merge subdicts or nested lists (yet).

For deeper nested objects use [dunder merge](environment_variables.html#nested-keys-in-dictionaries-via-environment-variables).

### Global merge

```bash
export MERGE_ENABLED_FOR_DYNACONF=true
```

or put it in your `.env` file then Dynaconf will automatically merge all existing variables.

> **BEWARE**: Using `MERGE_ENABLED_FOR_DYNACONF` can lead to unexpected results because you do not have granular control of what is being merged or overwritten so the recommendation is to use other options.

## More examples

Take a look at the [example](https://github.com/rochacbruno/dynaconf/tree/master/example) folder to see some examples of use with different file formats and features.
