import os
from dynaconf import constants as ct
from dynaconf import default_settings
from dynaconf.loaders import (
    yaml_loader, toml_loader, json_loader, ini_loader, py_loader
)
from dynaconf.utils.parse_conf import false_values


def default_loader(obj, defaults=None):
    defaults = defaults or {}
    default_settings_values = {
        key: value
        for key, value
        in default_settings.__dict__.items()
        if key.isupper()
    }

    all_keys = list(default_settings_values.keys()) + list(defaults.keys())

    for key in all_keys:
        value = defaults.get(key, default_settings_values.get(key))
        obj.logger.debug("default_loader:loading: %s:%s", key, value)
        obj.set(key, value)

    # start dotenv to get default env vars from there
    # check overrides in env vars
    default_settings.start_dotenv(obj)
    for key in all_keys:
        env_value = obj.get_environ(key, '_not_found')
        if env_value != '_not_found':
            obj.logger.debug(
                "default_loader:overriding from envvar: %s:%s",
                key, env_value
            )
            obj.set(key, env_value, tomlfy=True)


def settings_loader(obj, settings_module=None, env=None,
                    silent=True, key=None, filename=None):
    """Loads from defined settings module, path or yaml"""
    obj.logger.debug('executing settings_loader: %s', settings_module)
    settings_module = settings_module or obj.settings_module
    if not settings_module:  # pragma: no cover
        return

    if not isinstance(settings_module, (list, tuple)):
        files = settings_module.split(',')
    else:
        files = [settings_module]

    obj.logger.debug("files %s", files)

    if filename is not None:
        files.append(filename)

    for mod_file in files:
        # can be set to multiple files settings.py,settings.yaml,...

        # Cascade all loaders
        loaders = [
            {'ext': ct.YAML_EXTENSIONS, 'name': 'YAML', 'loader': yaml_loader},
            {'ext': ct.TOML_EXTENSIONS, 'name': 'TOML', 'loader': toml_loader},
            {'ext': ct.INI_EXTENSIONS, 'name': 'INI', 'loader': ini_loader},
            {'ext': ct.JSON_EXTENSIONS, 'name': 'JSON', 'loader': json_loader},
        ]

        for loader in loaders:
            if mod_file.endswith(loader['ext']):
                obj.logger.debug(
                    "Trying to load {0}:{1}".format(loader['name'], mod_file)
                )
                loader['loader'].load(
                    obj,
                    filename=mod_file,
                    env=env,
                    silent=silent,
                    key=key
                )
                continue

        if mod_file.endswith(ct.ALL_EXTENSIONS):
            continue

        # must be Python file or module

        obj.logger.debug("Trying to load Python module {}".format(mod_file))

        # load from default defined module settings.py or .secrets.py if exists
        py_loader.load(obj, mod_file, key=key)

        # load from the current env e.g: development_settings.py
        env = env or obj.current_env
        if mod_file.endswith('.py'):
            dirname = os.path.dirname(mod_file)
            filename, extension = os.path.splitext(
                os.path.basename(mod_file)
            )
            new_filename = "{0}_{1}{2}".format(
                env.lower(), filename, extension
            )
            env_mod_file = os.path.join(
                dirname, new_filename
            )
            global_filename = "{0}_{1}{2}".format(
                'global', filename, extension
            )
            global_mod_file = os.path.join(
                dirname, global_filename
            )
        else:
            env_mod_file = "{0}_{1}".format(
                env.lower(), mod_file
            )
            global_mod_file = "{0}_{1}".format(
                'global', mod_file
            )

        py_loader.load(
            obj,
            env_mod_file,
            identifier='py_{0}'.format(env.upper()),
            silent=True,
            key=key
        )

        # load from global_settings.py
        py_loader.load(
            obj,
            global_mod_file,
            identifier='py_global',
            silent=True,
            key=key
        )


def enable_external_loaders(obj):
    """Enable external service loaders like VAULT_ and REDIS_"""
    for name, loader in ct.EXTERNAL_LOADERS.items():
        enabled = getattr(
            obj,
            '{}_FOR_DYNACONF_ENABLED'.format(name.upper()),
            False
        )
        if (
              enabled and
              enabled not in false_values and
              loader not in obj.LOADERS_FOR_DYNACONF
            ):  # noqa
            obj.LOADERS_FOR_DYNACONF.append(loader)
