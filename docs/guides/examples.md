# Examples

## Supported file formats

### TOML

```
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

```
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

```
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

```
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

```
DEBUG=true
SERVER="flaskdynaconf.com"
PORT=6666
MESSAGE="Dynaconf works like a charm with Flask and .env"
TEST_RULE='/flask_with_ini'
```

## More examples

Take a look at [example/](https://github.com/rochacbruno/dynaconf/tree/master/example) for more examples.
