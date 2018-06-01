# coding: utf-8
from dynaconf.utils.files import find_file
from dynaconf.utils import raw_logger


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

    def __init__(self, obj, env, identifier, extensions,
                 file_reader, string_reader):
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
                {'ident': identifier}
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
            split_files = filename.split(',')
            if all([f.endswith(self.extensions) for f in split_files]):  # noqa
                files = split_files  # it is a ['file.ini', ...]
            else:  # it is a single ini string
                files = [filename]
        else:  # it is already a list/tuple
            files = filename

        # add the [default] env
        env_list = [self.obj.get('DEFAULT_ENV_FOR_DYNACONF')]

        # compatibility with older versions that still uses [dynaconf] as
        # [default] env
        global_env = self.obj.get('GLOBAL_ENV_FOR_DYNACONF')
        if global_env not in env_list:
            env_list.append(global_env)

        # add the current [env]
        if self.env not in env_list:
            env_list.append(self.env)

        # add the [global] env
        env_list.append('GLOBAL')

        # load all envs
        self._read(files, env_list, silent, key)

    def _read(self, files, envs, silent=True, key=None):
        for source_file in files:
            if source_file.endswith(self.extensions):  # pragma: no cover
                try:
                    source_data = self.file_reader(
                        open(find_file(source_file))
                    )
                    self.obj.logger.debug('{}_loader: {}'.format(
                        self.identifier, source_file))
                except IOError:
                    self.obj.logger.debug(
                        '{}_loader: {} (Ignored, file not Found)'.format(
                            self.identifier, source_file)
                    )
                    source_data = None
            else:
                # for tests it is possible to pass string
                source_data = self.string_reader(source_file)

            if not source_data:
                continue

            source_data = {
                k.lower(): value
                for k, value
                in source_data.items()
            }

            for env in envs:

                data = {}
                try:
                    data = source_data[env.lower()]
                except KeyError:
                    if env not in (self.obj.get('GLOBAL_ENV_FOR_DYNACONF'),
                                   'GLOBAL'):
                        message = '%s_loader: %s env not defined in %s' % (
                            self.identifier, env, source_file)
                        if silent:
                            self.obj.logger.warning(message)
                        else:
                            raise KeyError(message)
                    continue

                if env != self.obj.get('DEFAULT_ENV_FOR_DYNACONF'):
                    identifier = "{0}_{1}".format(self.identifier, env.lower())
                else:
                    identifier = self.identifier

                if not key:
                    self.obj.update(data, loader_identifier=identifier)
                elif key in data:
                    self.obj.set(key, data.get(key),
                                 loader_identifier=identifier)

                self.obj.logger.debug(
                    '{}_loader: {}: {}'.format(
                        self.identifier,
                        env.lower(),
                        list(data.keys()) if 'secret' in source_file else data
                    )
                )
