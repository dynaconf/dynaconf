# Django Extension

Dynaconf a drop in replacement to `django.conf.settings` 
This an extension makes your `app.config` in Flask to be a `dynaconf` instance.


In your django project's `settings.py` include:

```python
INSTALLED_APPS = [
    'dynaconf.contrib.django_dynaconf',
    ...
]
```

> **NOTE**: The extension must be included as the first INSTALLED_APP of the list

Now create your `settings.{py|yaml|toml|ini|json}` in your project's root directory
(the same folder where `manage.py` is located)

Now **django.conf.settings** will work as a `dynaconf.settings` instance and **DJANGO_** will
be the global prefix to export environment variables.

```bash
export DJANGO_DEBUG=true
export DJANGO_INTVALUE=1
```

It is recommended that all the **django's** internal config vars should be kept
in the `settings.py` of your project, then application specific values your can 
place in dynaconf's `settings.toml` in the root (same folder as manage.py).
You can override settings.py values in the dynaconf settings file.

> **NOTE**: To use `$ dynaconf` CLI the `DJANGO_SETTINGS_MODULE` must be defined and the cli must be called
> from the same directory where manage.py is placed.
