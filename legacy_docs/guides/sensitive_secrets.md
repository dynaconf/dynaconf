# Sensitive secrets

## Using .secrets files

To safely store sensitive data Dynaconf also searches for a `.secrets.{toml|py|json|ini|yaml}` file to look for data like tokens and passwords.

example `.secrets.toml`:

```ini
[default]
password = "sek@987342$"
```

The secrets file supports all the **environment** definitions supported in the **settings** file.

> **IMPORTANT**: The reason to use a `.secrets.*` file is the ability to omit this file when committing to the repository so a recommended `.gitignore` should include `.secrets.*` line.

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
VAULT_TOKEN_FOR_DYNACONF="myroot"
```

Now you can have keys like `PASSWORD` and `TOKEN` defined in the vault and
dynaconf will read it.

To write a new secret you can use http://localhost:8200 web admin and write keys
under the `/secret/dynaconf/< env >` secret database.

You can also use the Dynaconf writer via console:

```bash
# writes {'password': 123456} to secret/dynaconf/default
$ dynaconf write vault -s password=123456  

# writes {'password': 123456, 'username': 'admin'} to secret/dynaconf/default
$ dynaconf write vault -s password=123456 -s username=admin

# writes {'password': 555555} to secret/dynaconf/development
$ dynaconf write vault -s password=555555  -e development

# writes {'password': 777777, 'username': 'admin'} to secret/dynaconf/production
$ dynaconf write vault -s password=777777 -s username=produser -e production
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

```bash
export SECRETS_FOR_DYNACONF=/path/to/secrets.toml{json|py|ini|yaml}
```

If that variable exists in your environment then Dynaconf will also load it.
