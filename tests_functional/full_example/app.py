# Dynaconf read settings from ENV vars, redis server, conf files and more....
# this part should be done in O.S not in Python
# $export DYNACONF_HOSTNAME=host.com
# $export DYNACONF_PORT='@int 5000'
# or save to REDIS, yaml, json, ini etc...
from __future__ import annotations

import os

from dynaconf import settings

# Now read dynamic settings in your Python code
# you import only the 'settings' object always from dynaconf module

os.environ["DYNACONF_WORKS"] = "full_example"
os.environ["DYNACONF_HOSTNAME"] = "host.com"
os.environ["DYNACONF_PORT"] = "@int 5000"
os.environ["DYNACONF_VALUE"] = "@float 42.1"
os.environ["DYNACONF_ALIST"] = '@json ["item1", "item2", "item3"]'
os.environ["DYNACONF_ADICT"] = '@json {"key": "value"}'
os.environ["DYNACONF_DEBUG"] = (
    "@bool true"  # on, enabled, 1, active accepted as keyword here
)

# Now when reading settings they will be get from your sources dynamically
# defined data types are casted (but you can also do explicitly if want)
# read more in https://github.com/dynaconf/dynaconf

print("You server is:")
print(settings.HOSTNAME)

print("\nThe port is:")
print(settings.PORT)
print(type(settings.PORT))

print("\nThe value is:")
print(settings.VALUE)
print(type(settings.VALUE))

print("\nThe debug is:")
print(settings.DEBUG)
print(type(settings.DEBUG))

print("\nThe list is:")
print(settings.ALIST)
print(len(settings.ALIST))
print(type(settings.ALIST))

print("\nThe dict is:")
print(settings.ADICT)
print(settings.ADICT.keys())
print(type(settings.ADICT))


print("\nThe value that may not exist can have a default :")
print(settings.get("FOO", default="bar"))

print("\nThe host for default :")
print(settings.HOSTNAME)

print("\nDotted path lookup value :")
print(settings("ADICT.KEY"))

print(settings.WORKS)

print("\nDotted path set value :")
print(settings.set("ONE.TWO", "value"))


assertions = {
    "WORKS": "full_example",
    "HOSTNAME": "host.com",
    "PORT": 5000,
    "VALUE": 42.1,
    "ALIST": ["item1", "item2", "item3"],
    "ADICT": {"key": "value"},
    "ONE": {"TWO": "value"},
}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
