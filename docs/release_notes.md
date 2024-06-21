# Release Notes

## Dynaconf 3.1.1

This release is more about bug fixes and improvements,
we included a full [diagram](https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1&title=Dynaconf#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D11krXcDr67FGci_f36FZO-hiL08z4FuL9%26export%3Ddownload) of the library to help contributors.

### Vendoring

Dynaconf doesn't have dependencies because the main libraries used have
been vendored. In addition to the vendoring process (which followed the guidelines
regarding licensing and structure), all the vendored libraries have been minified to
save space on the distribution.

Ideally the vendored libraries will be upgraded on-demand only when a new security
or important bug fix is released on the respective vendored repository.

Python-box is an exception since the goal is to remove the dependency and implement
its basic features within dynaconf/DynaBox type.

### Cleanups

We made flake8 more strict and removed some unused imports and variables.

### Variable interpolation

The mechanism to evaluate `Lazy` values has been refactored and now `@format` and
`@jinja` values can be used within dictionaries and lists in any nesting levels.

### Validators

Fixed a problem when multiple combined validators are registered and fixed
duplication of ValidationError messages.

All names in a must_exist clause are now tested, instead of stopping validation on the
first failure.

### Fixes

- Cli now accepts dotted keys ex: `dynaconf -i config.settings list -k foo.bar.zaz`
- boto is now optional for vault authentication
- a `.formatter` attribute lookup was conflicting with Django logging so argument has
been renamed.
- box_settings made optional to DynaBox
- Included an example of SOPS custom loader
- `settings.set` is fixed so it now can set dotted attrs directly `settings.FOO = 1`
- Fix a problem on object_merge to allow keys with same name
- Added username and password to Redis
- Lots of typos on docs

## Dynaconf 3.1.0

### Providing default or computed values


Validators can be used to provide default or computed values.

#### Default values

```py
Validator("FOO", default="A default value for foo")
```

Then if not able to load the values from files or environment this default value will be set for that key.


#### Computed values

Sometimes you need some values to be computed by calling functions, just pass a callable to the `default` argument.

```py

Validator("FOO", default=my_function)

```

then

```py

def my_function(settings, validator):
    return "this is computed during validation time"

```

If you want it to be lazy evaluated

```py

from dynaconf.utils.parse_conf import empty, Lazy

Validator("FOO", default=Lazy(empty, formatter=my_function))

```

## Dynaconf 3.0.0

In Dynaconf 3.0.0 we introduced some improvements and with
those improvements it comes some **breaking changes.**

Some of the changes were discussed on the **1st Dynaconf community meeting** [video is available](https://www.twitch.tv/videos/657033043) and [meeting notes #354](https://github.com/dynaconf/dynaconf/issues/354).


## Improvements

- Validators now implements `|` and `&` operators to allow `Validator() &| Validator()` and has more `operations` available such as `len_eq, len_min, len_max, startswith` [#353](https://github.com/dynaconf/dynaconf/pull/353).
- First level variables are now allowed to be `lowercase` it is now possible to access `settings.foo` or `settings.FOO` [#357](https://github.com/dynaconf/dynaconf/pull/357).
- All Dependencies are now vendored, so when installing Dynaconf is not needed to install any dependency.
- Dynaconf configuration options are now aliased so when creating an instance of `LazySettings|FlaskDynaconf|DjangoDynaconf` it is now possible to pass instead of `ENVVAR_PREFIX_FOR_DYNACONF` just `envvar_prefix` and this lowercase alias is now accepted.
- Fixed bugs in `merge` and deprecated the `@reset` token.
- Added implementation for `__dir__` to allow auto complete for terminal and IDEs.
- Add option to override mount point for vault server.
- `LazySettings` is now aliased to `Dynaconf`
- `Dynaconf` class now accepts a parameter `validators=[Validator, ...]` that will be immediately evaluated when passed.

## Breaking Changes

> **NOTE 1** `from dynaconf import settings` will keep working until version `4.0.x` to allow users to migrate gradually without having breaking changes but it will raise some DeprecationWarnings.


> **NOTE 2** If you are using `FLASK` or `DJANGO` plugins there will be no breaking change on the framework settings, **a.k.a your project will keep working fine!**.


#### `dynaconf.settings` global settings instance is now deprecated.

Users are now supposed to create their own instance of `settings` instead of using the deprecated `from dynaconf import settings`.

**project/config.py**
```python
from dynaconf import Dynaconf

settings = Dynaconf(**options)
```

and then in your program you do `from project.config import settings` instead of `from dynaconf import settings`.

The `**options` are any of the [dynaconf config options](configuration.md)

ex:

```python
settings = Dynaconf(
    settings_file=["settings.toml", ".secrets.toml"],
    envvar_prefix="MYPROJECT"
)
```

> With the above instance your `settings` will load data from those 2 `.toml` files and also environment variables prefixed with `MYPROOJECT` e.g: `export MYPROJECT_FOO=1`


#### Dynaconf is now envless by default.

Historically Dynaconf worked in a multi layered environments for
loading data from files, so you were supposed to have a file like:

```toml
[default]
key = 'value'

[production]
key = 'value'
```

**Now starting on 3.0.0** the environments are disabled by default, so the same file can be created as.

```toml
key = 'value'
```

And you can still have the environments but only if you explicit specify it when creating your instance.


To have the previous behavior supporting all environments from the first level of a file.

```python
settings = Dynaconf(
    environments=True
)
```

or to strictly specify your environments.

```python
settings = Dynaconf(
    environments=["default", "production", "testing", "xyz"],
)
```

Once it is defined all the other functionalities still works such as.

```bash
export ENV_FOR_DYNACONF=production myprogram.py
```

#### Automatic load of `settings.*` files are disabled by default.

Starting on 3.x Dynaconf will now only load files passed explicitly to **settings_file** option when creating the instance or specified as env var **SETTINGS_FILE_FOR_DYNACONF**.

When creating the settings instance the file **paths** or **globs** should be specified unless you want only env vars and external loaders to be loaded.

Single file


```py
settings = Dynaconf(
    settings_file="settings.toml",
)
```

Or multiple files.


```py
settings = Dynaconf(
    settings_file=["settings.toml", "path/*.yaml"],
)
```

Dynaconf will respect the exact order informed by you on the `settings_file` parameter.

> **NOTE** the parameters `preload`, `includes` and `secret` continues to work in the same way as before.
> **NOTE** the parameters `preload`, `includes` and `secret` continues to work in the same way as before.

#### Load of dotenv `.env` is now disabled by default.

Dynaconf will **NO MORE** automatically load the data from `.env` file and will do that only
if `load_dotenv=True` is provided.


```py
settings = Dynaconf(
    load_dotenv=True
)
```

BY default it keeps searching for files in the current `PROJECT_ROOT` named `.env` and the `dotenv_path` accepts a relative path such as `.env` or  `path/to/.env`

#### DEBUG Logging is now completely removed

There is no more `logging` or `debug` messages being printed, so the variable `DEBUG_LEVEL` has no more effect.


## Coming in 3.1.x

- Support for Pydantic BaseSettings for Validators.
- Support for replacement of `toml` parser on envvars loader.
