# dynaconf
Dynamic config load for Python


# install
```
pip install dynaconf
```

# define your settings module

```
export DYNACONF_SETTINGS_MODULE=myproject.settings
or
export DYNACONF_SETTINGS_MODULE=myproject.production_settings
```

# you can export extra values

```
export DYNACONF_DATABASE='mysql://....'
export DYNACONF_SYSTEM_USER='admin'
export DYNACONF_FOO='bar'
```

Or define all your settings as env_vars starting with **DYNACONF_**

# Example

```
export DYNACONF_SETTINGS_MODULE=myproject.settings
```

### file: myproject/settings.py
```python
NAME = 'Bruno'
```

### file:app.py
```python

from dynaconf import settings

print settings.NAME
print settings.DATABASE
print settings.SYSTEM_USER
print settings.get('FOO')
```

### then

```
python app.py

Bruno
mysql://..
admin
bar
```

> This was inspired by django.conf.settings
