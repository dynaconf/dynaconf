# Flask Extension

Dynaconf provides a drop in replacement for `app.config` 
This an extension makes your `app.config` in Flask to be a `dynaconf` instance.

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

Now the `app.config` will work as a `dynaconf.settings` and **FLASK_** will be the
global prefix for exporting environment variables.

```bash
export FLASK_DEBUG=true
export FLASK_INTVALUE=1
```

The working environment will also respect the `FLASK_ENV` variable, so `FLASK_ENV=development` to work 
in development mode or `FLASK_ENV=production` to switch to production.

> **NOTE**: To use `$ dynaconf` CLI the `FLASK_APP` must be defined.
