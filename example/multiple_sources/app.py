from dynaconf import settings

print("Read from settings.py:", settings.PYTHON_VAR)  # noqa
print("Read from settings.yaml:", settings.YAML_VAR)  # noqa
print("Read from settings.yml:", settings.YML_VAR)  # noqa
print("Read from settings.toml:", settings.TOML_VAR)  # noqa
print("Read from settings.tml:", settings.TML_VAR)  # noqa
print("Read from settings.ini:", settings.INI_VAR)  # noqa
print("Read from settings.conf:", settings.CONF_VAR)  # noqa
print("Read from settings.properties:", settings.PROPERTIES_VAR)  # noqa
print("Read from settings.json:", settings.JSON_VAR)  # noqa
print("Read from .env:", settings.ENV_VAR)  # noqa
