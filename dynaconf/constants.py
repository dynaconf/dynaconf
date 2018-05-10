# pragma: no cover
INI_EXTENSIONS = ('.ini', '.conf', '.properties',)
TOML_EXTENSIONS = ('.toml', '.tml',)
YAML_EXTENSIONS = ('.yaml', '.yml',)
JSON_EXTENSIONS = ('.json',)

ALL_EXTENSIONS = INI_EXTENSIONS + TOML_EXTENSIONS + YAML_EXTENSIONS + JSON_EXTENSIONS  # noqa

EXTERNAL_LOADERS = {
    'ENV': 'dynaconf.loaders.env_loader',
    'REDIS': 'dynaconf.loaders.redis_loader',
    'VAULT': 'dynaconf.loaders.vault_loader',
}
