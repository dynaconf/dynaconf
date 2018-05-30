# Flask Extension

Dynaconf provides a drop in replacement for `app.config`.

As Flask encourages the composition by overriding the `config_class` attribute this extension follows the [patterns of Flask](http://flask.pocoo.org/docs/0.12/patterns/subclassing/) and turns your Flask's `app.config` in to a `dynaconf` instance.

## Initialize the extension

Initialize the **FlaskDynaconf** extension in your `app`

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

> You can optionally use `init_app` as well.

## Use `FLASK_` environment variables

Then the `app.config` will work as a `dynaconf.settings` instance and `FLASK_` will be the global prefix for exporting environment variables.

Example:

```bash
export FLASK_DEBUG=true              # app.config.DEBUG
export FLASK_INTVALUE=1              # app.config['INTVALUE']
export FLASK_MAIL_SERVER='host.com'  # app.config.get('MAIL_SERVER')
```

## Settings files

You can also have settings files for your Flask app, in the root directory (the same where you execute `flask run`) put your `settings.toml` and `.secrets.toml` files and then define your environments `[default]`, `[development]` and `[production]`.

To switch the working environment the `FLASK_ENV` variable can be used, so `FLASK_ENV=development` to work
in development mode or `FLASK_ENV=production` to switch to production.

> **IMPORTANT**: To use `$ dynaconf` CLI the `FLASK_APP` must be defined.

IF you don't want to manually create your config files take a look at the [CLI](cli.html)
