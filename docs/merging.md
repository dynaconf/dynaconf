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

Each `__` is parsed as a level traversing thought dict keys. read more in [environment variables](/envvars/#nested-keys-in-dictionaries-via-environment-variables)

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


### Nested keys in dictionaries via environment variables.

> **New in 2.1.0**
> 
> This is useful for `Django` settings.

Lets say you have a configuration like this:

`settings.py`

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'module.foo.engine',
        'ARGS': {'timeout': 30}
    }
}
```

And  now you want to change the values of `ENGINE` to `other.module`, via environment variables you can use the format `${ENVVAR_PREFIX}_${VARIABLE}__${NESTED_ITEM}__${NESTED_ITEM}`

Each `__` (dunder, a.k.a *double underline*) denotes access to nested elements in a dictionary.

So 

```py
DATABASES['default']['ENGINE'] = 'other.module'
```

Can be expressed as environment variables as:

```bash
export DYNACONF_DATABASES__default__ENGINE=other.module
```

> **NOTE**: if you are using Django extension then the prefix will be `DJANGO_` instead of `DYNACONF_` and the same if you are using `FLASK_` or a custom prefix if you have customized the `ENVVAR_PREFIX`.

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 30}
    }
}
```

> **IMPORTANT** lower case keys are respected only on *nix systems, unfortunately Windows environment variables are case insensitive and Python reads it as all upper cases, that means that if you are running on Windows the dictionary can have only upper case keys.

Now if you want to add a new item to `ARGS` key:

```bash
export DYNACONF_DATABASES__default__ARGS__retries=10
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 30, 'retries': 10}
    }
}
```

and you can also pass a `toml` like dictionary to be merged with existing `ARGS` key using `@merge` token.

> **new in 3.0.0**

```bash
# as a toml (recommended)
export DYNACONF_DATABASES__default__ARGS='@merge {timeout=50, size=1}'
# OR as a json
export DYNACONF_DATABASES__default__ARGS='@merge {"timeout": 50, "size": 1}'
# OR as plain key pair
export DYNACONF_DATABASES__default__ARGS='@merge timeout=50,size=1'
```

will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'retries': 10, 'timeout': 50, 'size': 1}
    }
}
```

Now if you want to clean an existing nested attribute you can just assign the new value.

```bash
# As a TOML empty dictionary `"{}"`
export DYNACONF_DATABASES__default__ARGS='{}'
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {}
    }
}
```

```bash
# As a TOML  dictionary (recommended)
export DYNACONF_DATABASES__default__ARGS='{timeout=90}'
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module',
        'ARGS': {'timeout': 90}
    }
}
```

And if in any case you need to completely remove that key from the dictionary:

```bash
export DYNACONF_DATABASES__default__ARGS='@del'
```

This will result in

```py
DATABASES = {
    'default': {
        'NAME': 'db',
        'ENGINE': 'other.module'
    }
}
```

### Using the `dynaconf_merge` mark on configuration files.

> **New in 2.0.0**

To merge exported variables there is the **dynaconf_merge** tokens, example:

Your main settings file (e.g `settings.toml`) has an existing `DATABASE` dict setting on `[default]` env.

Now you want to contribute to the same `DATABASE` key by adding new keys, so you can use `dynaconf_merge` at the end of your dict:

In specific `[envs]`

```cfg
[default]
database = {host="server.com", user="default"}

[development]
database = {user="dev_user", dynaconf_merge=true}
```

or

> New in **2.2.0**

```cfg
[default]
database = {host="server.com", user="default"}

[development.database]
dynaconf_merge = {user="dev_user"}
```

In an environment variable use `@merge` token:

> **New in 2.2.0**

```bash
# Toml formatted envvar
export DYNACONF_DATABASE='@merge {password=1234}'
```

or `dunder` (recommended)

```bash
# Toml formatted envvar
export DYNACONF_DATABASE__PASSWORD=1234
```

The end result will be on `[development]` env:

```python
settings.DATABASE == {'host': 'server.com', 'user': 'dev_user', 'password': 1234}
```


> **BEWARE**: Using `MERGE_ENABLED_FOR_DYNACONF` can lead to unexpected results because you do not have granular control of what is being merged or overwritten so the recommendation is to use other options.

### Known caveats

The **dynaconf_merge** and **@merge** functionalities works only for the first level keys, it will not merge subdicts or nested lists (yet).

For deeper nested objects use [dunder merge](/envvars/#nested-keys-in-dictionaries-via-environment-variables).



## More examples

Take a look at the [example](https://github.com/rochacbruno/dynaconf/tree/master/example) folder to see some examples of use with different file formats and features.
