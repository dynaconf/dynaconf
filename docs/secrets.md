# Sensitive secrets

## Using .secrets files

To safely store sensitive data Dynaconf also searches for a `.secrets.{toml|py|json|ini|yaml}` file to look for data like tokens and passwords.

example `.secrets.toml`:

```ini
password = "sek@987342$"
```

!!! tip
    When `environments=True` is enabled, The secrets file supports all the **environment** definitions supported in the **settings** file.


!!! info
    The reason to use a `.secrets.*` file is the ability to omit this file when committing to the repository so a recommended `.gitignore` should include `.secrets.*` line.

## Using Vault server

The [vaultproject.io/](https://www.vaultproject.io/) is a key:value store for secrets and Dynaconf can load
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
# Specify the secrets engine for kv, default is 1
VAULT_KV_VERSION_FOR_DYNACONF=1
# Authenticate with token https://www.vaultproject.io/docs/auth/token
VAULT_TOKEN_FOR_DYNACONF="myroot"
# Authenticate with AppRole https://www.vaultproject.io/docs/auth/approle
VAULT_ROLE_ID_FOR_DYNACONF="role-id"
VAULT_SECRET_ID_FOR_DYNACONF="secret-id"
# Authenticate with AWS IAM https://www.vaultproject.io/docs/auth/aws
# The IAM Credentials can be retrieved from the standard providers: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
VAULT_AUTH_WITH_IAM_FOR_DYNACONF=True
VAULT_AUTH_ROLE_FOR_DYNACONF="vault-role"
# Authenticate with root token
VAULT_ROOT_TOKEN_FOR_DYNACONF="root-token"
# If you want to perform (can be useful when using orphan VAULT_TOKEN_FOR_DYNACONF)
VAULT_TOKEN_RENEW_FOR_DYNACONF="true"
```

Or pass it to the `Dynaconf` instance.

```py
settings = Dynaconf(
    environment=True,
    vault_enabled=True,
    vault={'url': 'http://localhost:8200', 'token': 'myroot'} # recommended to keep as env var.
)
```

Now you can have keys like `PASSWORD` and `TOKEN` defined in the vault and
dynaconf will read it.

To write a new secret you can use http://localhost:8200 web admin and write keys
under the `/secret/dynaconf/< env >` secret database.

You can also use the Dynaconf writer via console:

```bash
# writes {'password': 123456} to secret/dynaconf/default
$ dynaconf -i config.settings write vault -s password=123456

# writes {'password': 123456, 'username': 'admin'} to secret/dynaconf/default
$ dynaconf -i config.settings write vault -s password=123456 -s username=admin

# writes {'password': 555555} to secret/dynaconf/development
$ dynaconf -i config.settings write vault -s password=555555  -e development

# writes {'password': 777777, 'username': 'admin'} to secret/dynaconf/production
$ dynaconf -i config.settings write vault -s password=777777 -s username=produser -e production
```

then you can access values normally in your program

```py
from dynaconf import settings

settings.PASSWORD == 555555  # if ENV_FOR_DYNACONF is the default `development`
settings.USERNAME == 'admin'  # if ENV_FOR_DYNACONF is the default `development`

settings.PASSWORD == 777777  # if ENV_FOR_DYNACONF is `production`
settings.USERNAME == 'produser'  # if ENV_FOR_DYNACONF is `production`
```

You can also ask settings to be loaded from specific env with `from_env` method:

```py
settings.from_env('production').PASSWORD == 777777
settings.from_env('production').USERNAME == 'produser'
```

## Additional secrets file (for CI, jenkins etc.)

It is common to have an extra `secrets` file that is available only when running on specific CI environment like `Jenkins`, usually there will be an environment variable pointing to the file.

On Jenkins it is done on job settings by exporting the `secrets` information.

Dynaconf can handle this via `SECRETS_FOR_DYNACONF` environment variable.

ex:

```py
settings = Dynaconf(secrets="path/to/secrets.toml")
```

or

```bash
export SECRETS_FOR_DYNACONF=/path/to/secrets.toml{json|py|ini|yaml}
```

If that variable exists in your environment then Dynaconf will also load it.

---
## External Storage

An external storage is needed in some programs for scenarios like:

1) Having a single storage for settings and distribute across multiple instances
2) The need to change settings on the fly without redeploying or restarting the app.
3) Storing sensitive values in a safe sealed **Vault**

### Using REDIS

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
REDIS_USERNAME_FOR_DYNACONF=<ACL username>(optional)
REDIS_PASSWORD_FOR_DYNACONF=<password>(optional)
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

> if you want to skip type casting, write as string instead of PORT=1234 use PORT="'1234'".

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

## Custom Storages

Do you want to store settings in other databases like NoSQL, Relational Databases or other services?

Please see how to [extend dynaconf](advanced.md) to add your custom loaders.
