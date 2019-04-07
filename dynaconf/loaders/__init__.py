import os
from dynaconf import constants as ct
from dynaconf import default_settings
from dynaconf.loaders import (
    yaml_loader, toml_loader, json_loader, ini_loader, py_loader
)
from dynaconf.utils import deduplicate
from dynaconf.utils.parse_conf import false_values


def default_loader(obj, defaults=None):
    """Loads default settings and check if there are overridings
    exported as environment variables"""
    defaults = defaults or {}
    default_settings_values = {
        key: value
        for key, value
        in default_settings.__dict__.items()  # noqa
        if key.isupper()
    }

    all_keys = deduplicate(
        list(defaults.keys()) + list(default_settings_values.keys())
    )

    for key in all_keys:
        if not obj.exists(key):
            value = defaults.get(key, default_settings_values.get(key))
            obj.logger.debug("default_loader: loading: %s:%s", key, value)
            obj.set(key, value)

    # start dotenv to get default env vars from there
    # check overrides in env vars
    default_settings.start_dotenv(obj)

    # Deal with cases where a custom ENV_SWITCHER_IS_PROVIDED
    # Example: Flask and Django Extensions
    env_switcher = defaults.get(
        'ENV_SWITCHER_FOR_DYNACONF', 'ENV_FOR_DYNACONF'
    )

    for key in all_keys:
        if key not in default_settings_values.keys():
            continue

        env_value = obj.get_environ(
            env_switcher if key == 'ENV_FOR_DYNACONF' else key,
            default='_not_found'
        )

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
    if filename is None:
        settings_module = settings_module or obj.settings_module
        if not settings_module:  # pragma: no cover
            return

        if isinstance(settings_module, (list, tuple)):
            files = list(settings_module)
        else:
            files = settings_module.split(',')
    else:
        files = [filename]

    secrets_file = obj.get('SECRETS_FOR_DYNACONF', None)
    if secrets_file is not None:
        if isinstance(secrets_file, (list, tuple)):
            files.extend(secrets_file)
        else:
            files.extend(secrets_file.split(','))

    found_files = []
    modules_names = []
    for item in files:
        if item.endswith(ct.ALL_EXTENSIONS + ('.py',)):
            p_root = obj._root_path or (
                os.path.dirname(found_files[0]) if found_files else None
            )
            found = obj.find_file(item, project_root=p_root)
            if found:
                found_files.append(found)
        else:
            # a bare python module name w/o extension
            modules_names.append(item)

    enabled_core_loaders = obj.get('CORE_LOADERS_FOR_DYNACONF')

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
            if loader['name'] not in enabled_core_loaders:
                continue

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

        if 'PY' not in enabled_core_loaders:
            # pyloader is disabled
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
