import io
import os

from dynaconf.utils import build_env_list
from dynaconf.utils import ensure_a_list
from dynaconf.utils import raw_logger
from dynaconf.utils import upperfy


logger = raw_logger()


class BaseLoader(object):
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
            logger.warning(
                "%(ident)s support is not installed in your environment. "
                "`pip install dynaconf[%(ident)s]`",
                {"ident": identifier},
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

        self.obj._loaded_files.extend(files)

        env_list = build_env_list(self.obj, self.env)

        # load all envs
        self._read(files, env_list, silent, key)

    def _read(self, files, envs, silent=True, key=None):
        for source_file in files:
            if source_file.endswith(self.extensions):
                try:
                    with io.open(
                        source_file,
                        encoding=self.obj.get(
                            "ENCODING_FOR_DYNACONF", "utf-8"
                        ),
                    ) as open_file:
                        source_data = self.file_reader(open_file)
                    self.obj.logger.debug(
                        "{}_loader: {}".format(self.identifier, source_file)
                    )
                except IOError:
                    self.obj.logger.debug(
                        "{}_loader: {} (Ignored, file not Found)".format(
                            self.identifier, source_file
                        )
                    )
                    source_data = None
            else:
                # for tests it is possible to pass string
                source_data = self.string_reader(source_file)

            if not source_data:
                continue

            # env name is checked in lower
            source_data = {
                k.lower(): value for k, value in source_data.items()
            }

            # is there a `dynaconf_merge` on top level of file?
            file_merge = source_data.get("dynaconf_merge")

            # all lower case for comparison
            base_envs = [
                # DYNACONF or MYPROGRAM
                (self.obj.get("ENVVAR_PREFIX_FOR_DYNACONF") or "").lower(),
                # DEFAULT
                self.obj.get("DEFAULT_ENV_FOR_DYNACONF").lower(),
                # default active env unless ENV_FOR_DYNACONF is changed
                "development",
                # backwards compatibility for global
                "dynaconf",
                # global that rules all
                "global",
            ]

            for env in envs:
                env = env.lower()  # lower for better comparison
                data = {}
                try:
                    data = source_data[env] or {}
                except KeyError:
                    if env not in base_envs:
                        message = "%s_loader: %s env not defined in %s" % (
                            self.identifier,
                            env,
                            source_file,
                        )
                        if silent:
                            self.obj.logger.warning(message)
                        else:
                            raise KeyError(message)
                    continue

                if env != self.obj.get("DEFAULT_ENV_FOR_DYNACONF").lower():
                    identifier = "{0}_{1}".format(self.identifier, env)
                else:
                    identifier = self.identifier

                # data 1st level keys should be transformed to upper case.
                data = {upperfy(k): v for k, v in data.items()}
                if key:
                    key = upperfy(key)

                is_secret = "secret" in source_file

                self.obj.logger.debug(
                    "{}_loader: {}[{}]{}".format(
                        self.identifier,
                        os.path.split(source_file)[-1],
                        env,
                        list(data.keys()) if is_secret else data,
                    )
                )

                # is there a `dynaconf_merge` inside an `[env]`?
                file_merge = file_merge or data.pop("DYNACONF_MERGE", False)

                if not key:
                    self.obj.update(
                        data,
                        loader_identifier=identifier,
                        is_secret=is_secret,
                        merge=file_merge,
                    )
                elif key in data:
                    self.obj.set(
                        key,
                        data.get(key),
                        loader_identifier=identifier,
                        is_secret=is_secret,
                        merge=file_merge,
                    )
