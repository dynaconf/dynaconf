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
- `{this.DB_NAME}` is the same as `settings.DB_NAME` or `settings["DB_NAME"]`

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

The main difference is that Jinja allows some Python expressions to be evaluated such as `{% for, if, while %}` and also supports calling methods and has lots of filters like `| lower`.

Jinja supports its built-in filters listed in [Builtin Filters Page](http://jinja.palletsprojects.com/en/master/templates/#builtin-filters) and Dynaconf includes additional filters for `os.path` module: `abspath`. `realpath`, `relpath`, `basename` and `dirname` and usage is like: `VALUE = "@jinja {{this.FOO | abspath}}"`
