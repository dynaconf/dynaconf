# Testing

For testing it is recommended to just switch to `testing` environment and read the same config files.

`settings.toml`
```toml
[default]
value = "On Default"

[testing]
value = "On Testing"
```

`program.py`
```python
from dynaconf import settings

print(settings.VALUE)
```

```bash
ENV_FOR_DYNACONF=testing python program.py
```

Then your `program.py` will print `"On Testing"` red from `[testing]` environment.


## Pytest

For pytest it is common to create fixtures to provide pre-configured settings object or to configure the settings before
all the tests are collected.

Examples available on [https://github.com/rochacbruno/dynaconf/tree/master/example/pytest_example](https://github.com/rochacbruno/dynaconf/tree/master/example/pytest_example)

With `pytest` fixtures it is recommended to use the `FORCE_ENV_FOR_DYNACONF` isntead of just `ENV_FOR_DYNACONF` because it has precedence.

### A python program

`settings.toml` with the `[testing]` environment.

```toml
[default]
VALUE = "On Default"

[testing]
VALUE = "On Testing"
```

`app.py` that reads that value from current environment.
```py
from dynaconf import settings


def return_a_value():
    return settings.VALUE
```

`tests/conftest.py` with a fixture to force `settings` to run pointing to `[testing]` environment.

```py
import pytest
from dynaconf import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
```

`tests/test_dynaconf.py` to assert that the correct environment is loaded

```py
from app import return_a_value


def test_dynaconf_is_in_testing_env():
    assert return_a_value() == "On Testing"
```

### A Flask program

`settings.toml` with the `[testing]` environment.

```toml
[default]
VALUE = "On Default"

[testing]
VALUE = "On Testing"
```

`src.py` that has a Flask application factory

```py
from flask import Flask
from dynaconf.contrib import FlaskDynaconf


def create_app(**config):
    app = Flask(__name__)
    FlaskDynaconf(app, **config)
    return app

```

`tests/conftest.py` with a fixture to provide `app` dependency injection to all the tests,
And force this `app` to point to `[testing]` config environment.

```py
import pytest
from src import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
    return app
```

`tests/test_flask_dynaconf.py` to assert that the correct environment is loaded

```py
def test_dynaconf_is_on_testing_env(app):
    assert app.config["VALUE"] == "On Testing"
    assert app.config.current_env == "testing"
```

## Mocking

But it is common in unit tests to `mock` some objects and you may need in rare cases to mock the `dynaconf.settings` when running your tests.

```python
from dynaconf.utils import DynaconfDict
mocked_settings = DynaconfDict({'FOO': 'BAR'})
```

DynaconfDict is a dict like obj that can be populated from a file:

```python
from dynaconf.loaders import toml_loader
toml_loader.load(mocked_settings, filename='my_file.toml', env='testing')
```
