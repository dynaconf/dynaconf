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

# MERGE TESTS

print("The dict should include all files", settings.A_BIG_DICT)  # noqa

keys = (
    "settings.py",
    "development_settings.py",
    "global_settings.py",
    "settings.yaml",
    "settings.yml",
    "settings.toml.default",
    "settings.toml.global",
    "settings.tml.default",
    "settings.tml.global",
    "settings.ini",
    "settings.conf",
    "settings.properties",
    "settings.json.default",
    "settings.json.global",
    ".env",
)

for key in keys:
    assert key in settings.A_BIG_DICT.file
    assert key in settings("A_BIG_DICT").file
    assert key in settings("A_BIG_DICT")["file"]
    assert key in settings("A_BIG_DICT").get("file")
    assert key in settings.A_BIG_DICT["file"]
    assert key in settings.A_BIG_DICT.get("file")


print("Big nest", settings.A_BIG_DICT.nested_1.nested_2.nested_3.nested_4)  # noqa

assert settings.A_BIG_DICT.nested_1.nested_2.nested_3.nested_4 == {
    "json": True,
    "yaml": True,
    "toml": True,
    "py": True,
}
