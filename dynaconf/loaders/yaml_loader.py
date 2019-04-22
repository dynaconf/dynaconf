import io
from pathlib import Path
from warnings import warn

from dynaconf import default_settings
from dynaconf.constants import YAML_EXTENSIONS
from dynaconf.loaders.base import BaseLoader
from dynaconf.utils import object_merge

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source file.

    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Optional custom filename to load
    :return: None
    """
    if yaml is None:  # pragma: no cover
        BaseLoader.warn_not_installed(obj, "yaml")
        return

    # Resolve the loaders
    # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
    # Possible values are `safe_load, full_load, unsafe_load, load`
    yaml_reader = getattr(yaml, obj.get("YAML_LOADER_FOR_DYNACONF"), yaml.load)
    if yaml_reader.__name__ == "unsafe_load":  # pragma: no cover
        warn(
            "yaml.unsafe_load is deprecated."
            " Please read https://msg.pyyaml.org/load for full details."
            " Try to use full_load or safe_load."
        )

    loader = BaseLoader(
        obj=obj,
        env=env,
        identifier="yaml",
        extensions=YAML_EXTENSIONS,
        file_reader=yaml_reader,
        string_reader=yaml_reader,
    )
    loader.load(filename=filename, key=key, silent=silent)


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        with io.open(
            str(settings_path), encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as open_file:
            object_merge(yaml.full_load(open_file), settings_data)

    with io.open(
        str(settings_path),
        "w",
        encoding=default_settings.ENCODING_FOR_DYNACONF,
    ) as open_file:
        yaml.dump(settings_data, open_file)
