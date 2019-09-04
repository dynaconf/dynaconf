# External storages

An external storage is needed in some programs for scenarios like:

1) Having a single storage for settings and distribute across multiple instances
2) The need to change settings on the fly without redeploying or restarting the app (see [Feature Flags](feature_flag.html))
3) Storing sensitive values in a safe sealed **Vault**

## Using REDIS

1. Run a Redis server installed or via docker:

```bash
$ docker run -d -p 6379:6379 redis
```

2. Install support for redis in dynaconf

```bash
$ pip install dynaconf[redis]
```

3. In your `.env` file or in exported environment variables define:

```bash
REDIS_ENABLED_FOR_DYNACONF=true
REDIS_HOST_FOR_DYNACONF=localhost
REDIS_PORT_FOR_DYNACONF=6379
```

You can now write variables direct in to a redis hash named `DYNACONF_< env >` for example:

- `DYNACONF_DEFAULT`: default values
- `DYNACONF_DEVELOPMENT`: loaded only when `ENV_FOR_DYNACONF=development` (default)
- `DYNACONF_PRODUCTION`: loaded only when `ENV_FOR_DYNACONF=production`
- `DYNACONF_CUSTOM`: loaded only when `ENV_FOR_DYNACONF=custom`

You can also use the redis writer

```bash
$ dynaconf write redis -v name=Bruno -v database=localhost -v port=1234
```

The above data will be recorded in redis as a hash:

```
DYNACONF_DEFAULT {
    NAME='Bruno'
    DATABASE='localhost'
    PORT='@int 1234'
}
```

If you want to write to specific `env` pass the `-e` option.

```bash
$ dynaconf write redis -v name=Bruno -v database=localhost -v port=1234 -e production
```

The above data will be recorded in redis as a hash:

```
DYNACONF_PRODUCTION {
    NAME='Bruno'
    DATABASE='localhost'
    PORT='@int 1234'
}
```

Then to access that values you can set `export ENV_FOR_DYNACONF=production` or directly via `settings.from_env('production').NAME`

> if you want to skip type casting, write as string intead of PORT=1234 use PORT="'1234'".

Data is read from redis and another loaders only once when `dynaconf.settings` is first accessed
or when `from_env`, `.setenv()` or `using_env()` are invoked.

You can access the fresh value using **settings.get_fresh(key)**

There is also the **fresh** context manager

```python
from dynaconf import settings

print(settings.FOO)  # this data was loaded once on import

with settings.fresh():
    print(settings.FOO)  # this data is being freshly reloaded from source

print(settings.get('FOO', fresh=True))  # this data is being freshly reloaded from source
```

And you can also force some variables to be **fresh** setting in your setting file

```python
FRESH_VARS_FOR_DYNACONF = ['MYSQL_HOST']
```

or using env vars

```bash
export FRESH_VARS_FOR_DYNACONF='["MYSQL_HOST", "OTHERVAR"]'
```

Then

```python
from dynaconf import settings

print(settings.FOO)         # This data was loaded once on import

print(settings.MYSQL_HOST)  # This data is being read from redis imediatelly!
```

## Using Hashicorp Vault to store secrets

Read more in [Using Vault Server section](sensitive_secrets.html)

## Custom Storages

Do you want to store settings in other databases like NoSQL, Relational Databases or other services?

Please see how to [extend dynaconf](extend.html) to add your custom loaders.
