from __future__ import annotations

from dynaconf import settings

print("Read from settings.py:", settings.PYTHON_VAR)  # noqa

# BY DEFAULT 'development' is the current env
print("Read from development_settings.py:", settings.PYTHON_DEV_VAR)  # noqa

# If ENV_FOR_DYNACONF=production is in envvars so
# print("Read from production_settings.py:", settings.PYTHON_PROD_VAR)  # noqa

# global_ overrides previous configs
print("Read from global_settings.py:", settings.PYTHON_GLOBAL_VAR)  # noqa


print("Read from settings.yaml:", settings.YAML_VAR)  # noqa
print("Read from settings.yml:", settings.YML_VAR)  # noqa
print("Read from settings.toml:", settings.TOML_VAR)  # noqa
print("Read from settings.tml:", settings.TML_VAR)  # noqa
print("Read from settings.ini:", settings.INI_VAR)  # noqa
print("Read from settings.conf:", settings.CONF_VAR)  # noqa
print("Read from settings.properties:", settings.PROPERTIES_VAR)  # noqa
print("Read from settings.json:", settings.JSON_VAR)  # noqa
print("Read from .env:", settings.ENV_VAR)  # noqa
print("Read from .env:", settings.WORKS)  # noqa


assertions = {
    "YAML_VAR": True,
    "YML_VAR": True,
    "TOML_VAR": True,
    "INI_VAR": "1",
    "CONF_VAR": "1",
    "PROPERTIES_VAR": "1",
    "JSON_VAR": True,
    "ENV_VAR": True,
    "WORKS": "multiple_sources",
}

for key, value in assertions.items():
    found = settings.get(key)
    assert found == getattr(settings, key)
    assert found == value, f"expected: {key}: [{value}] found: [{found}]"
