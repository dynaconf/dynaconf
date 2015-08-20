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

# casting values from envvars

Sometimes you need to set some values as specific types, boolean, integer, float or lists and dicts.

built in casts

- @int (as_int)
- @bool (as_bool)
- @float (as_float)
- @json (as_json)

> @json / as_json  will use json to load a Python object from string, it is useful to get lists and dictionaries. The return is always a Python object.

strings does not need converters.

You have 2 ways to use the casts.

### Casting on declaration

Just start your ENV settigs with this

```
export DYNACONF_DEFAULT_THEME='material'
export DYNACONF_DEBUG='@bool True'
export DYNACONF_DEBUG_TOOLBAR_ENABLED='@bool False'
export DYNACONF_PAGINATION_PER_PAGE='@int 20'
export DYNACONF_MONGODB_SETTINGS='@json {"DB": "quokka_db"}'
export DYNACONF_ALLOWED_EXTENSIONS='@json ["jpg", "png"]'
```

Starting the settings values with @ will make dynaconf.settings to cast it in the time od load.

### Casting on access

```
export DYNACONF_USE_SSH='yes'

from dynaconf import settings

use_ssh = settings.get('USE_SSH', cast='@bool')
# or
use_ssh = settings('USE_SSH', cast='@bool')
# or
use_ssh = settings.as_bool('USE_SSH')

print use_ssh

True
```

### more examples

```
export DYNACONF_USE_SSH='enabled'

export DYNACONF_ALIST='@json [1,2,3]'
export DYNACONF_ADICT='@json {"name": "Bruno"}'
export DYNACONF_AINT='@int 42'
export DYNACONF_ABOOL='@bool on'
export DYNACONF_AFLOAT='@float 42.5'
```

```python

from dynaconf import settings
settings.configure()

# original value
settings('USE_SSH')
'enabled'

# cast as bool
settings('USE_SSH', cast='@bool')
True

# also cast as bool
settings.as_bool('USE_SSH')
True

# cast defined in declaration '@bool on'
settings.ABOOL
True

# cast defined in declaration '@json {"name": "Bruno"}'
settings.ADICT
{u'name': u'Bruno'}

# cast defined in declaration '@json [1,2,3]'
settings.ALIST
[1, 2, 3]

# cast defined in decalration '@float 42.5'
settings.AFLOAT
42.5

# cast defined in declaration '@int 42'
settings.AINT
42

```


> This was inspired by django.conf.settings
