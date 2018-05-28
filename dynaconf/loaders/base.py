# coding: utf-8
from dynaconf.utils.files import find_file


class BaseLoader(object):
    """Base loader for dynaconf source files."""

    def __init__(self, obj, env, identifier, module_is_loaded, extensions,
                 file_reader, string_reader):
        """Instantiates a loader for different sources

        Arguments:
            obj {[LazySettings]} -- [Dynaconf settings]
            env {[string]} -- [the current env to be loaded defaults to
                [development]]
            identifier {[string]} -- [identifier ini, yaml, json, py, toml]
            module_is_loaded {[bool]} -- [bool or module object]
            extensions {[list]} -- [List of extensions with dots ['.a', '.b']]
            file_reader {[callable]} -- [reads file return dict]
            string_reader {[callable]} -- [reads string return dict]
        """
        self.obj = obj
        self.env = env or obj.current_env
        self.identifier = identifier
        self.module_is_loaded = module_is_loaded
        self.extensions = extensions
        self.file_reader = file_reader
        self.string_reader = string_reader

    def load(self, filename=None, key=None, silent=True):
        """
        Reads and loads in to "self.obj" a single key or all keys from source
        """
        if self.module_is_loaded is None:  # pragma: no cover
            self.obj.logger.warning(
                "%(ident)s support is not installed in your environment.\n"
                "To use this loader you have to install it with\n"
                "pip install dynaconf[%(ident)s]",
                {'ident': self.identifier}
            )
            return

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
        self.read(files, env_list, silent, key)

    def read(self, files, envs, silent=True, key=None):
        for source_file in files:
            if source_file.endswith(self.extensions):  # pragma: no cover
                self.obj.logger.debug('Trying to load {}'.format(source_file))
                try:
                    source_data = self.file_reader(
                        open(find_file(source_file))
                    )
                except IOError as e:
                    self.obj.logger.debug(
                        "Unable to load file {}: {}".format(
                            source_file, str(e)
                        )
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
                    message = '%s env not defined in %s' % (
                        env, source_file)
                    if silent:
                        self.obj.logger.warning(message)
                    else:
                        raise KeyError(message)

                if env != self.obj.get('DEFAULT_ENV_FOR_DYNACONF'):
                    identifier = "{0}_{1}".format(self.identifier, env.lower())
                else:
                    identifier = self.identifier

                if not key:
                    self.obj.update(data, loader_identifier=identifier)
                elif key in data:
                    self.obj.set(key, data.get(key),
                                 loader_identifier=identifier)
