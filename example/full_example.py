# Dynaconf read settings from ENV vars, redis server, conf files and more....
# this part should be done in O.S not in Python
# $export DYNACONF_HOSTNAME=host.com
# $export DYNACONF_PORT='@int 5000'
# or save to REDIS, yaml, json, ini etc...

import os

# Now read dynamic settings in your Python code
# you import only the 'settings' object always from dynaconf module
from dynaconf import settings

os.environ['DYNACONF_WORKS'] = 'full_example'
os.environ['DYNACONF_HOSTNAME'] = 'host.com'
os.environ['DYNACONF_PORT'] = '@int 5000'
os.environ['DYNACONF_VALUE'] = '@float 42.1'
os.environ['DYNACONF_ALIST'] = '@json ["item1", "item2", "item3"]'
os.environ['DYNACONF_ADICT'] = '@json {"key": "value"}'
os.environ['DYNACONF_DEBUG'] = '@bool true'  # on, enabled, 1, active accepted as keyword here
os.environ['PROJECT1_HOSTNAME'] = 'otherhost.com'

# Now when reading settings they will be get from your sources dynamically
# defined data types are casted (but you can also do explicitly if want)
# read more in https://github.com/rochacbruno/dynaconf

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
print(settings.get('FOO', default='bar'))

print("\nNamespaces Support :")
with settings.using_namespace('PROJECT1'):
    print("\nThe host for project1 :")
    print(settings.HOSTNAME)

print("\nThe host for default :")
print(settings.HOSTNAME)

print("\nNamespaces Support :")
with settings.using_namespace('PROJECT1'):
    print("\nThe host for project1 :")
    print(settings.HOSTNAME)

print("\nThe host for default :")
print(settings.HOSTNAME)

print(settings.WORKS)
