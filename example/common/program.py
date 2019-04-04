# Take as example a program which connects to a database


def connect(server, port, username, password):
    """This function might be something coming from your ORM"""
    print('-' * 79)
    print('Connecting to: {}'.format(server))
    print('At port: {}'.format(port))
    print('Using username: {}'.format(username))
    print('Using password: {}'.format(password))
    print('-' * 79)
    # imagine it connects here...


# The `connect` function needs to take the server, username and value
# and those values must be read from settings.toml config file

# The `password` is sensitive so it comes from .secrets.toml file
# or even better it may come from vaultproject.io

# Dynaconf takes care of it!

from dynaconf import settings  # noqa

print(settings.dynaconf_banner)

print('#' * 79)
print('\n* The settings are defined in .toml files\n')
print('$ cat settings.toml')
print(open(settings.find_file('./settings.toml')).read())
print('$ cat .secrets.toml')
print(open(settings.find_file('.secrets.toml')).read())

print('#' * 79)
print('\n* Acessing settings defined in .toml files\n')
print('By default dynaconf will always work in "development" env')
print('Take a look at settings.toml and .secrets.toml')
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
assert settings.SERVER == 'devserver.com'
assert settings.PORT == 5555
assert settings.USERNAME == 'admin'
assert settings.PASSWORD == 'SuperSecretDev'

print('#' * 79)
print('\n* Working on a different environment\n')
print('To switch the env export the ENV_FOR_DYNACONF variable')
print('$ export ENV_FOR_DYNACONF=production')
print('Now reading settings from PRODUCTION env:')
# this next line is not needed in your program, it is the same as `export ENV_FOR_DYNACONF..`
import os; os.environ['ENV_FOR_DYNACONF'] = 'production'; settings.reload()  # noqa
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
assert settings.SERVER == 'prodserver.com'
assert settings.PORT == 5555
assert settings.USERNAME == 'admin'
assert settings.PASSWORD == 'SuperSecretProd'

print('#' * 79)
print('\n* Switching environments\n')
print('We can easily switch to staging env')
print('$ export ENV_FOR_DYNACONF=staging')
# this next line is not needed in your program, it is the same as `export ENV_FOR_DYNACONF..`
os.environ['ENV_FOR_DYNACONF'] = 'staging'; settings.reload()  # noqa
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
assert settings.SERVER == 'stagserver.com'
assert settings.PORT == 5555
assert settings.USERNAME == 'admin'
assert settings.PASSWORD == 'SuperSecret'  # will use the [default]


print('#' * 79)
print('\n* Environments and Custom Environments\n')
print('Dynaconf works with 4 predefined envs:')
print('  [development](the default), [production], [staging], [testing]')
print('There is also the pseudo envs')
print('  [default](default values) and [global](overrides every value)')
print('It is also possible to define custom envs')
print('$ export ENV_FOR_DYNACONF=mycustomenv')
# this next line is not needed in your program, it is the same as `export ENV_FOR_DYNACONF..`
os.environ['ENV_FOR_DYNACONF'] = 'mycustomenv'; settings.reload()  # noqa
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
assert settings.SERVER == 'customserver.com'
assert settings.PORT == 5555
assert settings.USERNAME == 'admin'
assert settings.PASSWORD == 'SuperSecret'  # will use the [default]

print('#' * 79)
print('\n* Default and Global settings\n')
print('The env [global] is to override values defined in any other env')
print('It means a value in [global] will always take high precedence')
print('To override any value in [global] just put the value in .toml file')
print('Or via envvars export a value with DYNACONF_ prefix')
print('$ export DYNACONF_USERNAME="NewUsername"')
print('You can also put the value in .env file"')
# this next line is not needed in your program, it is the same as `export DYNACONF_USERNAME..`
os.environ['DYNACONF_USERNAME'] = 'NewUsername'; settings.reload()  # noqa
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
print('settings.EXTRA_VALUE = ', settings.EXTRA_VALUE)
assert settings.SERVER == 'customserver.com'
assert settings.PORT == 5555
assert settings.USERNAME == 'NewUsername'
assert settings.PASSWORD == 'SuperSecret'  # will use the [default]
assert settings.EXTRA_VALUE == 'Value defined in .env'

print('#' * 79)
print('\n* Using environment variables at program call\n')
print('Another common pattern is defining the value in the program call')
print('$ DYNACONF_USERNAME=YetAnotherUser python program.py')
# this next line is not needed in your program, it is the same as `export DYNACONF_USERNAME..`
os.environ['DYNACONF_USERNAME'] = 'YetAnotherUser'; settings.reload()  # noqa
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
assert settings.SERVER == 'customserver.com'
assert settings.PORT == 5555
assert settings.USERNAME == 'YetAnotherUser'
assert settings.PASSWORD == 'SuperSecret'  # will use the [default]


print('#' * 79)
print('\n* Type definitions for environment variables\n')
print('Note that the PORT variable must be integer')
print('And envvars are by default string typed')
print('Dynaconf allows type definition on exporting an envvar')
print('$ export DYNACONF_PORT="@int 8888"')
# this next line is not needed in your program, it is the same as `export DYNACONF_USERNAME..`
os.environ['DYNACONF_PORT'] = '@int 8888'; settings.reload()  # noqa
connect(settings.SERVER, settings.PORT, settings.USERNAME, settings.PASSWORD)
assert settings.SERVER == 'customserver.com'
assert settings.PORT == 8888
assert settings.USERNAME == 'YetAnotherUser'
assert settings.PASSWORD == 'SuperSecret'  # will use the [default]
print('DONT WORRY: if you dont like the `@type` strategy you can disable it')
print('and perform the explicit cast when reading')
print('>>> connect(..., settings.as_int("PORT"), ...)')
print('types: @int|.as_int, @float|.as_float, @bool|.as_bool and @json|.as_json')

print('#' * 79)
print('\n* There is more!\n')
print('Dynaconf can switch environments programatically with context managers.')
print('Dynaconf has extensions for Flask and Django.')
print('Dynaconf can read values from yaml, ini, json and py files.')
print('Dynaconf can load sensitive values from vaultproject.io.')
print('Dynaconf can load dynamic fresh values from Redis server (useful for feature flagging).')
print('#' * 79)
print(settings.dynaconf_banner)
print('Learn more at http://github.com/rochacbruno/dynaconf')


with settings.using_env('testing'):
    assert settings.SERVER == 'testserver.com'

assert settings.SERVER == 'customserver.com'
