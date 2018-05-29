# External storages

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

You can now write variables direct in to a redis hash named `DYNACONF_< env >`

You can also use the redis writer

```bash
$ dynaconf write redis -v name=Bruno -v database=localhost -v port=1234
```

The above data will be recorded in redis as a hash:

```
DYNACONF_DYNACONF {
    NAME='Bruno'
    DATABASE='localhost'
    PORT='@int 1234'
}
```

> if you want to skip type casting, write as string intead of PORT=1234 use PORT="'1234'".

Data is read from redis and another loaders only once when `dynaconf.settings` is first accessed
or when `.setenv()` or `using_env()` are invoked.

You can access the fresh value using **settings.get_fresh(key)**

There is also the **fresh** context manager

```python
from dynaconf import settings

print(settings.FOO)  # this data was loaded once on import

with settings.fresh():
    print(settings.FOO)  # this data is being freshly reloaded from source
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

The https://www.vaultproject.io/ is a key:value store for secrets and Dynaconf can load
variables from a Vault secret.

1. Run a vault server

Run a Vault server installed or via docker:

```bash
$ docker run -d -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' -p 8200:8200 vault
```

2. Install support for vault in dynaconf

```bash
$ pip install dynaconf[vault]
```

3. In your `.env` file or in exported environment variables define:

```bash
VAULT_ENABLED_FOR_DYNACONF=true
VAULT_URL_FOR_DYNACONF="http://localhost:8200"
VAULT_TOKEN_FOR_DYNACONF="myroot"
```

Now you can have keys like `PASSWORD` and `TOKEN` defined in the vault and
dynaconf will read it.

To write a new secret you can use http://localhost:8200 web admin and write keys
under the `/secret/dynaconf` secret database.

You can also use the Dynaconf writer via console

```bash
$ dynaconf write vault -s password=123456
```
