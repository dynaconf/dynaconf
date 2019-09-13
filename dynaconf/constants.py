# pragma: no cover
INI_EXTENSIONS = (".ini", ".conf", ".properties")
TOML_EXTENSIONS = (".toml", ".tml")
YAML_EXTENSIONS = (".yaml", ".yml")
JSON_EXTENSIONS = (".json",)

ALL_EXTENSIONS = (
    INI_EXTENSIONS + TOML_EXTENSIONS + YAML_EXTENSIONS + JSON_EXTENSIONS
)  # noqa

EXTERNAL_LOADERS = {
    "ENV": "dynaconf.loaders.env_loader",
    "VAULT": "dynaconf.loaders.vault_loader",
    "REDIS": "dynaconf.loaders.redis_loader",
}

DJANGO_PATCH = """
# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://dynaconf.readthedocs.io/en/latest/guides/django.html
import dynaconf  # noqa
settings = dynaconf.DjangoDynaconf(__name__)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
 """
