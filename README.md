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

# Namespace support

When you are working with multiple projects using the same environment maybe you want to use different namespaces for ENV vars based configs


```bash
export DYNACONF_DATABASE="DYNADB"
export PROJ1_DATABASE="PROJ1DB"
export PROJ2_DATABASE="PROJ2DB"
```

and then access them


```python
from dynaconf import settings

# configure() or configure('settingsmodule.path') is needed
# only when DYNACONF_SETINGS_MODULE is not defined
settings.configure()

# access default namespace settings
settings.DATABASE
'DYNADB'

# switch namespaces
settings.namespace('PROJ1')
settings.DATABASE
'PROJ1DB'

settings.namespace('PROJ2')
settings.DATABASE
'PROJ2DB'

# return to default, call it without args
settings.namespace()
settings.DATABASE
'DYNADB'
```

You can also use the context manager:

```python
settings.DATABASE
'DYNADB'

with settings.using_namespace('PROJ1'):
    settings.DATABASE
    'PROJ1DB'

with settings.using_namespace('PROJ2'):
    settings.DATABASE
    'PROJ2DB'

settings.DATABASE
'DYNADB'
```

> This was inspired by django.conf.settings
