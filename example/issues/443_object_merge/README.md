# [bug] Setting values being stripped out after merge

* created by @daviddavis on 2020-10-07 14:13:58 +0000 UTC

**Describe the bug**
I'm seeing where values are being stripped out of settings. This is on dynaconf 3.1.1 with Python 3.7.7.

**To Reproduce**
Run this code:

```python
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils import object_merge

existing_data = DynaBox({"DATABASES": {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2', 'HOST': 'localhost', 'PASSWORD': 'pulp', 'NAME': 'pulp', 'USER': 'pulp'}}})
new_data = DynaBox({'DATABASES': {'default': {'USER': 'postgres'}}})
split_keys = ['DATABASES', 'default', 'USER']
object_merge(old=existing_data, new=new_data, full_path=split_keys)
```

The output:

```
<Box: {'DATABASES': {'default': {'USER': 'postgres', 'ENGINE': 'django.db.backends.postgresql_psycopg2', 'HOST': 'localhost'}}}>
```

Notice that NAME and PASSWORD keys have been dropped.

**Expected behavior**
I would expect the final settings dict to be:

```
{"DATABASES": {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2', 'HOST': 'localhost', 'PASSWORD': 'pulp', 'NAME': 'pulp', 'USER': 'postgres'}}}
```

## Comments:

### comment by @rochacbruno on 2020-10-07 14:31:15 +0000 UTC

The bug is in

https://github.com/rochacbruno/dynaconf/blob/8998cac224a985dc8bb783f2a5abd71ff4e6769c/dynaconf/utils/__init__.py#L45

As all the values are `pulp` it is wrongly using `is` to compare and `"pulp" is "pulp"` will always be `True` regardless the key it is in.

```py
>>> s1 = "pulp"
>>> s2 = "pulp"
>>> s1 is s2
True
```

I will need to include the full path to the key on the comparison or change the `DynaBox` in a way that each value gets its own identity even if the value is the same.
