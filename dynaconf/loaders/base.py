import io
import warnings

from dynaconf.utils import build_env_list
from dynaconf.utils import ensure_a_list
from dynaconf.utils import upperfy


class BaseLoader:
    """Base loader for dynaconf source files.

    :param obj: {[LazySettings]} -- [Dynaconf settings]
    :param env: {[string]} -- [the current env to be loaded defaults to
      [development]]
    :param identifier: {[string]} -- [identifier ini, yaml, json, py, toml]
    :param extensions: {[list]} -- [List of extensions with dots ['.a', '.b']]
    :param file_reader: {[callable]} -- [reads file return dict]
    :param string_reader: {[callable]} -- [reads string return dict]
    """

    def __init__(
        self, obj, env, identifier, extensions, file_reader, string_reader
    ):
        """Instantiates a loader for different sources"""
        self.obj = obj
        self.env = env or obj.current_env
        self.identifier = identifier
        self.extensions = extensions
        self.file_reader = file_reader
        self.string_reader = string_reader

    @staticmethod
    def warn_not_installed(obj, identifier):  # pragma: no cover
        if identifier not in obj._not_installed_warnings:
            warnings.warn(
                f"{identifier} support is not installed in your environment. "
                f"`pip install dynaconf[{identifier}]`"
            )
        obj._not_installed_warnings.append(identifier)

    def load(self, filename=None, key=None, silent=True):
        """
        Reads and loads in to `self.obj` a single key or all keys from source

        :param filename: Optional filename to load
        :param key: if provided load a single key
        :param silent: if load erros should be silenced
        """
        filename = filename or self.obj.get(self.identifier.upper())
        if not filename:
            return

        if not isinstance(filename, (list, tuple)):
            split_files = ensure_a_list(filename)
            if all([f.endswith(self.extensions) for f in split_files]):  # noqa
                files = split_files  # it is a ['file.ext', ...]
            else:  # it is a single config as string
                files = [filename]
        else:  # it is already a list/tuple
            files = filename

        source_data = self.get_source_data(files)

        if self.obj.get("ENVIRONMENTS_FOR_DYNACONF") is False:
            self._envless_load(source_data, silent, key)
        else:
            self._load_all_envs(source_data, silent, key)

    def get_source_data(self, files):
        """Reads each file and returns source data for each file
        {"path/to/file.ext": {"key": "value"}}
        """
        data = {}
        for source_file in files:
            if source_file.endswith(self.extensions):
                try:
                    with io.open(
                        source_file,
                        encoding=self.obj.get(
                            "ENCODING_FOR_DYNACONF", "utf-8"
                        ),
                    ) as open_file:
                        content = self.file_reader(open_file)
                        self.obj._loaded_files.append(source_file)
                        if content:
                            data[source_file] = content
                except IOError as e:
                    if ".local." not in source_file:
                        warnings.warn(
                            f"{self.identifier}_loader: {source_file} "
                            f":{str(e)}"
                        )
            else:
                # for tests it is possible to pass string
                content = self.string_reader(source_file)
                if content:
                    data[source_file] = content
        return data

    def _envless_load(self, source_data, silent=True, key=None):
        """Load all the keys from each file without env separation"""
        for file_data in source_data.values():
            self._set_data_to_obj(file_data, self.identifier, key=key)

    def _load_all_envs(self, source_data, silent=True, key=None):
        """Load configs from files separating by each environment"""

        for file_data in source_data.values():

            # env name is checked in lower
            file_data = {k.lower(): value for k, value in file_data.items()}

            # is there a `dynaconf_merge` on top level of file?
            file_merge = file_data.get("dynaconf_merge")

            for env in build_env_list(self.obj, self.env):
                env = env.lower()  # lower for better comparison
                data = {}

                try:
                    data = file_data[env] or {}
                except KeyError:
                    if silent:
                        continue
                    raise

                if not data:
                    continue

                if env != self.obj.get("DEFAULT_ENV_FOR_DYNACONF").lower():
                    identifier = f"{self.identifier}_{env}"
                else:
                    identifier = self.identifier

                self._set_data_to_obj(data, identifier, file_merge, key)

    def _set_data_to_obj(
        self, data, identifier, file_merge=None, key=False,
    ):
        """Calls setttings.set to add the keys"""

        # data 1st level keys should be transformed to upper case.
        data = {upperfy(k): v for k, v in data.items()}
        if key:
            key = upperfy(key)

        # is there a `dynaconf_merge` inside an `[env]`?
        file_merge = file_merge or data.pop("DYNACONF_MERGE", False)

        if not key:
            self.obj.update(
                data, loader_identifier=identifier, merge=file_merge,
            )
        elif key in data:
            self.obj.set(
                key,
                data.get(key),
                loader_identifier=identifier,
                merge=file_merge,
            )
