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

# you can export extra values (or even define all as ENV vars)

```
export DYNACONF_DATABASE = 'mysql://....'
export DYNACONF_SYSTEM_USER = 'admin'
export DYNACONF_FOO = 'bar'
```

# having the settings file

## myproject/settings.py
```python
NAME = 'Bruno'
```

# use it

## ascript.py
```python

from dynaconf import settings

print settings.NAME
print settings.DATABASE
print settings.SYSTEM_USER
print setttings.get('FOO')
```

# So

```
python ascript.py
Bruno
mysql://..
admin
bar
```

> This was inspired by django.conf.settings
