# Sensitive secrets

## Using .secrets files

To safely store sensitive data Dynaconf also searches for a `.secrets.{toml|py|json|ini|yaml}` file to look for data like tokens and passwords.

example `.secrets.toml`:

```ini
[default]
password = "sek@987342$"
```

The secrets file supports all the **environment** definitions supported in the **settings** file.

> **IMPORTANT**: The reason to use a `.secrets.*` file is the ability to omit this file when commiting to the repository so a recommended `.gitignore` should include `.secrets.*` line.

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

You can also use the Dynaconf writer via console

```bash
$ dynaconf write vault -s password=123456
```

## Additional secrets file (for CI, jenkins etc.)

It is common to have an extra `secrets` file that is available only when running on specific CI environment like `Jenkins`, usually there will be an environment variable pointing to the file.

On Jenkins it is done on job settings by exporting the `secrets` information.

Dynaconf can handle this via `SECRETS_FOR_DYNACONF` environment variable.

ex:

```bash
export SECRETS_FOR_DYNACONF=/path/to/settings.toml{json|py|ini|yaml}
```

If that variable exists in your environment then Dynaconf will also load it.
