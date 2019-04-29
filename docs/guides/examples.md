# Examples

## Supported file formats

### TOML

```cfg
[default]
DEBUG = true
SERVER = "flaskdynaconf.com"
PORT = 6666
MESSAGE = "Dynaconf works like a charm with Flask and TOML"
TEST_RULE = '/flask_with_toml'

[development]
DEBUG = true
SERVER = "dev.flaskdynaconf.com"

[production]
DEBUG = false
SERVER = "prod.flaskdynaconf.com"
```

### YAML

```yaml
default:
  DEBUG: true
  SERVER: flaskdynaconf.com
  PORT: 6666
  MESSAGE: Dynaconf works like a charm with Flask and YAML
  TEST_RULE: /flask_with_yaml
development:
  DEBUG: true
  SERVER: dev.flaskdynaconf.com
production:
  DEBUG: false
  SERVER: prod.flaskdynaconf.com
```

### INI

```ini
[default]
DEBUG = true
SERVER = "flaskdynaconf.com"
PORT = 6666
MESSAGE = "Dynaconf works like a charm with Flask and INI"
TEST_RULE = '/flask_with_ini'

[development]
DEBUG = true
SERVER = "dev.flaskdynaconf.com"

[production]
DEBUG = false
SERVER = "prod.flaskdynaconf.com"
```

### JSON

```json
{
  "default": {
    "DEBUG": true,
    "SERVER": "flaskdynaconf.com",
    "PORT": 6666,
    "MESSAGE": "Dynaconf works like a charm with Flask and JSON",
    "TEST_RULE": "/flask_with_json"
  },
  "development": {
    "DEBUG": true,
    "SERVER": "dev.flaskdynaconf.com"
  },
  "production": {
    "DEBUG": false,
    "SERVER": "prod.flaskdynaconf.com"
  }
}
```

### PY

In python fils the `environment` is set by prefixing the file names

`settings.py`

```python
DEBUG = True
SERVER = "flaskdynaconf.com"
PORT = 6666
MESSAGE = "Dynaconf works like a charm with Flask and .py"
TEST_RULE = '/flask_with_ini'
```

`development_settings.py`

```python
DEBUG = True 
SERVER = "dev.flaskdynaconf.com"
```

`production_settings.py`

```python
DEBUG = False 
SERVER = "prod.flaskdynaconf.com"
```

### .env

`.env` allows only the `global` environment (overrides everything)

```bash
DEBUG=true
SERVER="flaskdynaconf.com"
PORT=6666
MESSAGE="Dynaconf works like a charm with Flask and .env"
TEST_RULE='/flask_with_ini'
```

## Using a default main config file plus variable settings file

On the `.env`

```bash
export SETTINGS_FILE_FOR_DYNACONF="default.toml"
```

The default file

```ini
[default]
variable1 = 'value1'
```

Now having specific settings per environment

Use cases:

- plugin based apps
- user specific settings
- dev specific settings

On the **user1** environment

```bash
export INCLUDES_FOR_DYNACONF='/path/to/user1_specific_settings.toml'
```

On the **user2** environment

```bash
export INCLUDES_FOR_DYNACONF='/path/to/user2_specific_settings.toml'
```

It can be a glob

```bash
export INCLUDES_FOR_DYNACONF='/path/to/config/*.toml'
```

And also supports having a `;` or `,` separated list of paths or globs.

## More examples

Take a look at [example/](https://github.com/rochacbruno/dynaconf/tree/master/example) for more examples.
