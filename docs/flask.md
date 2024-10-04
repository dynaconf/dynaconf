# Flask Extension

Dynaconf provides a drop in replacement for `app.config`.

As Flask encourages the composition by overriding the `config_class` attribute this extension follows the [patterns of Flask](https://flask.palletsprojects.com/en/2.3.x/patterns/subclassing/) and turns your Flask's `app.config` in to a `dynaconf` instance.

## Initialize the extension

Initialize the **FlaskDynaconf** extension in your `app`

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

> You can optionally use `init_app` as well.


## Compatibility mode

Dynaconf transform nested data structures to a new DynaBox instance, this is an
object that allows dot notation access such as `app.config.key.value.other`.
However this feature is incompatible with some Flask extensions, for example:
`Flask-Alembic`.

So in case you see a `BoxKeyError` when running your app with you can run it on
compatibility mode.

```python
FlaskDynaconf(app, compatibility_mode=True)
```

The downside is that now you cannot access nested elements using dot notation
but the usual access interface via dict subscription will work normally:
`app.config["KEY"]["value"]["other"]`

!!! info
    On Dynaconf 4.0 compatibility_mode will default to True when running
    on Flask.

## Use `FLASK_` environment variables

Then the `app.config` will work as a `dynaconf.settings` instance and `FLASK_` will be the global prefix for exporting environment variables.

Example:

```bash
export FLASK_DEBUG=true              # app.config.DEBUG
export FLASK_INTVALUE=1              # app.config['INTVALUE']
export FLASK_MAIL_SERVER='host.com'  # app.config.get('MAIL_SERVER')
```

You can also leverage custom environment variables just as in the default Dynaconf class, like so:

Example:

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app, envvar_prefix="PEANUT")
```

Now you can declare your variables with your custom prefix, and it will be normally available within Flask's native configuration `app.config`.

```bash
export PEANUT_DEBUG=true              # app.config.DEBUG
export PEANUT_INTVALUE=1              # app.config['INTVALUE']
export PEANUT_MAIL_SERVER='host.com'  # app.config.get('MAIL_SERVER')
```

!!! info
    Version 3.1.7 backwards was case sensitive on defining `ENVVAR_PREFIX` and would only accept uppsercase kwargs (different from `Dynaconf(envvar_prefix)`). Starting from version X.X.X, kwargs should be case insensitive to improve consistency between Dynaconf and Flask/Django extensions, while keeping backwards compatibility.

## Settings files

You can also have settings files for your Flask app, in the root directory (the same where you execute `flask run`) put your `settings.toml` and `.secrets.toml` files and then define your environments `[default]`, `[development]` and `[production]`.

To switch the working environment the `FLASK_ENV` variable can be used, so `FLASK_ENV=development` to work
in development mode or `FLASK_ENV=production` to switch to production.

> **IMPORTANT**: To use `$ dynaconf` CLI the `FLASK_APP` must be defined.

IF you don't want to manually create your config files take a look at the [CLI](cli.md)

## Loading Flask Extensions Dynamically

You can tell Dynaconf to load your Flask Extensions dynamically as long as the extensions follows the Patterns of Flask extensions.

The only requirement is that the extension must be a `callable` that accepts `app` as first argument. e.g: `flask_admin:Admin` or `custom_extension.module:instance.init_app` and of course the extension must be in Python namespace to be imported.

For extensions initialized just use an [entry point](https://packaging.python.org/specifications/entry-points/) object reference like: "flask_admin:Admin" or "extension.module:instance.init_app"

having a `settings.toml`

```toml
[default]
EXTENSIONS = [
  "flask_admin:Admin",
  "flask_bootstrap:Bootstrap",
  "custom_extension.module:init_app"
]
```

Considering an `app.py` like:

```py
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
flask_dynaconf = FlaskDynaconf(app, extensions_list="EXTENSIONS")
```

The above will immediately load all flask extensions listed on `EXTENSIONS` key on settings.

You can also load it lazily.

```py
# at any point in your app startup
app.config.load_extensions()
```

Optionally you can pass `load_extensions(key="OTHER_NAME")` pointing to your list of extensions.

It is also possible to use environment variables to set the extensions to be loaded.

```bash
# .env
export FLASK_EXTENSIONS="['flask_admin:Admin']"
```

The extensions will be loaded in order.

### Development extensions

It is also possible to have extensions that loads only for development environment.

```toml
[default]
EXTENSIONS = [
  "flask_admin:Admin",
  "flask_bootstrap:Bootstrap",
  "custom_extension.module:init_app"
]

[development]
EXTENSIONS = [
  "dynaconf_merge",
  "flask_debugtoolbar:DebugToolbar"
]
```

### Troubleshooting

If you find an issue regarding Flask not being able to load variables from .env file or not possible to import app or create_app please disable flask support for dotenv

```bash
export FLASK_SKIP_DOTENV=1
```
