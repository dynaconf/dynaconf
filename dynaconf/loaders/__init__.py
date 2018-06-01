import os
from dynaconf import constants as ct
from dynaconf import default_settings
from dynaconf.loaders import (
    yaml_loader, toml_loader, json_loader, ini_loader, py_loader
)
from dynaconf.utils.parse_conf import false_values
from dynaconf.utils.files import find_file


def default_loader(obj, defaults=None):
    """Loads default settings and check if there are overridings
    exported as environment variables"""
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
        obj.logger.debug("default_loader: loading: %s:%s", key, value)
        obj.set(key, value)

    # start dotenv to get default env vars from there
    # check overrides in env vars
    default_settings.start_dotenv(obj)
    for key in all_keys:
        env_value = obj.get_environ(key, '_not_found')
        if env_value != '_not_found':
            obj.logger.debug(
                "default_loader: overriding from envvar: %s:%s",
                key, env_value
            )
            obj.set(key, env_value, tomlfy=True)


def settings_loader(obj, settings_module=None, env=None,
                    silent=True, key=None, filename=None):
    """Loads from defined settings module

    :param obj: A dynaconf instance
    :param settings_module: A path or a list of paths e.g settings.toml
    :param env: Env to look for data defaults: development
    :param silent: Boolean to raise loading errors
    :param key: Load a single key if provided
    :param filename: optional filename to override the settings_module
    """
    settings_module = settings_module or obj.settings_module
    if not settings_module:  # pragma: no cover
        return

    if not isinstance(settings_module, (list, tuple)):
        files = settings_module.split(',')
    else:
        files = [settings_module]

    obj.logger.debug("Looking for %s", files)

    if filename is not None:
        files.append(filename)

    found_files = []
    modules_names = []
    for item in files:
        if item.endswith(ct.ALL_EXTENSIONS + ('.py',)):
            found = find_file(item)
            if found:
                found_files.append(found)
        else:
            # a bare python module name w/o extension
            modules_names.append(item)

    obj.logger.debug("Found files %s", found_files)

    for mod_file in (modules_names + found_files):
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
        # load from default defined module settings.py or .secrets.py if exists
        py_loader.load(obj, mod_file, key=key)

        # load from the current env e.g: development_settings.py
        env = env or obj.current_env
        if mod_file.endswith('.py'):
            if '.secrets.py' == mod_file:
                tmpl = ".{0}_{1}{2}"
                mod_file = 'secrets.py'
            else:
                tmpl = "{0}_{1}{2}"

            dirname = os.path.dirname(mod_file)
            filename, extension = os.path.splitext(
                os.path.basename(mod_file)
            )
            new_filename = tmpl.format(
                env.lower(), filename, extension
            )
            env_mod_file = os.path.join(
                dirname, new_filename
            )
            global_filename = tmpl.format(
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
    """Enable external service loaders like `VAULT_` and `REDIS_`
    looks forenv variables like `REDIS_ENABLED_FOR_DYNACONF`
    """
    for name, loader in ct.EXTERNAL_LOADERS.items():
        enabled = getattr(
            obj,
            '{}_ENABLED_FOR_DYNACONF'.format(name.upper()),
            False
        )
        if (
              enabled and
              enabled not in false_values and
              loader not in obj.LOADERS_FOR_DYNACONF
            ):  # noqa
            obj.logger.debug('loaders: Enabling %s', loader)
            obj.LOADERS_FOR_DYNACONF.insert(0, loader)
