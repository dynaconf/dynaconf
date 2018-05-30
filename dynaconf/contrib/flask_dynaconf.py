# coding: utf-8
import os
try:
    from flask.config import Config
    flask_installed = True
except ImportError:  # pragma: no cover
    flask_installed = False
    Config = object


from dynaconf import LazySettings


class FlaskDynaconf(object):
    """The arguments are.
    app = The created app
    dynaconf_args = Extra args to be passed to Dynaconf (validator for example)

    All other values are stored as config vars specially::

        ENV_FOR_DYNACONF = env prefix for your envvars to become settings
                            example:
                                export MYSITE_SQL_PORT='@int 5445'

                            with that exported to env you access using:
                                app.config.SQL_PORT
                                app.config.get('SQL_PORT')
                                app.config.get('sql_port')
                                # get is case insensitive
                                app.config['SQL_PORT']

                            Dynaconf uses `@int, @bool, @float, @json` to cast
                            env vars

        SETTINGS_MODULE_FOR_DYNACONF = The name of the module or file to use as
                                    default to load settings. If nothing is
                                    passed it will be `settings.*` or value
                                    found in `ENVVAR_FOR_DYNACONF`
                                    Dynaconf supports
                                    .py, .yml, .toml, ini, json

    ATTENTION: Take a look at `settings.yml` and `.secrets.yml` to know the
            required settings format.

    Settings load order in Dynaconf:

    - Load all defaults and Flask defaults
    - Load all passed variables when applying FlaskDynaconf
    - Update with data in settings files
    - Update with data in environmente vars `ENV_FOR_DYNACONF_`


    TOML files are very useful to have `envd` settings, lets say,
    `production` and `development`.

    You can also achieve the same using multiple `.py` files naming as
    `settings.py`, `production_settings.py` and `development_settings.py`
    (see examples/validator)

    Example::

        app = Flask(__name__)
        FlaskDynaconf(
            app,
            ENV_FOR_DYNACONF='MYSITE',
            SETTINGS_MODULE_FOR_DYNACONF='settings.yml',
            EXTRA_VALUE='You can add aditional config vars here'
        )

    Take a look at examples/flask in Dynaconf repository

    """
    def __init__(self, app=None, instance_relative_config=False,
                 dynaconf_instance=None, **kwargs):
        """kwargs holds initial dynaconf configuration"""
        if not flask_installed:  # pragma: no cover
            raise RuntimeError(
                "To use this extension Flask must be installed "
                "install it with: pip install flask"
            )
        self.kwargs = kwargs
        if 'GLOBAL_ENV_FOR_DYNACONF' not in kwargs:
            kwargs['GLOBAL_ENV_FOR_DYNACONF'] = 'FLASK'
        if 'ENV_FOR_DYNACONF' not in kwargs:
            kwargs['ENV_FOR_DYNACONF'] = os.environ.get(
                'FLASK_ENV', 'DEVELOPMENT').upper()
        self.dynaconf_instance = dynaconf_instance
        self.instance_relative_config = instance_relative_config
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """kwargs holds initial dynaconf configuration"""
        self.kwargs.update(kwargs)
        self.settings = self.dynaconf_instance or LazySettings(**self.kwargs)
        app.config = self.make_config(app)
        app.dynaconf = self.settings

    def make_config(self, app):
        root_path = app.root_path
        if self.instance_relative_config:  # pragma: no cover
            root_path = app.instance_path
        if self.dynaconf_instance:
            self.settings.update(self.kwargs)
        return DynaconfConfig(
            root_path=root_path,
            defaults=app.config,
            _settings=self.settings
        )


class DynaconfConfig(Config):
    """
    Settings load order in Dynaconf:

    - Load all defaults and Flask defaults
    - Load all passed variables when applying FlaskDynaconf
    - Update with data in settings files
    - Update with data in environmente vars `ENV_FOR_DYNACONF_`
    """

    def get(self, key, default=None):
        """Gets config from dynaconf variables
        if variables does not exists in dynaconf try getting from
        `app.config` to support runtime settings."""
        return self._settings.get(key, Config.get(self, key, default))

    def __init__(self, _settings, *args, **kwargs):
        """perform the initial load"""
        super(DynaconfConfig, self).__init__(*args, **kwargs)
        Config.update(self, _settings.store)
        self._settings = _settings

    def __getitem__(self, key):
        """
        Flask templates always expects a None when key is not found in config
        """
        return self.get(key)

    def __getattr__(self, name):
        """
        First try to get value from dynaconf then from Flask
        """
        try:
            return getattr(self._settings, name)
        except AttributeError:
            return self[name]

    def __call__(self, name, *args, **kwargs):
        return self.get(name, *args, **kwargs)
