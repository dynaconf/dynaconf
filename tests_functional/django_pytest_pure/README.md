# Reproduce pytest + dynaconf error

setup project
```
./setup.sh
```

run tests
```
./tests.sh
```

result
```python
=================================================================================================================================================== test session starts ====================================================================================================================================================
platform linux -- Python 3.6.9, pytest-5.4.3, py-1.10.0, pluggy-0.13.1
django: settings: project.settings (from ini)
rootdir: /home/alex/dje/django-pytest-dynaconf, inifile: pytest.ini
plugins: django-4.1.0
collected 1 item

app/tests/test_app.py E                                                                                                                                                                                                                                                                                              [100%]

========================================================================================================================================================== ERRORS ==========================================================================================================================================================
____________________________________________________________________________________________________________________________________________ ERROR at setup of test_admin_user _____________________________________________________________________________________________________________________________________________

request = <SubRequest '_django_db_marker' for <Function test_admin_user>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request):
        """Implement the django_db marker, internal to pytest-django.

        This will dynamically request the ``db``, ``transactional_db`` or
        ``django_db_reset_sequences`` fixtures as required by the django_db marker.
        """
        marker = request.node.get_closest_marker("django_db")
        if marker:
            transaction, reset_sequences = validate_django_db(marker)
            if reset_sequences:
                request.getfixturevalue("django_db_reset_sequences")
            elif transaction:
                request.getfixturevalue("transactional_db")
            else:
>               request.getfixturevalue("db")

venv/lib/python3.6/site-packages/pytest_django/plugin.py:436:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
venv/lib/python3.6/site-packages/pytest_django/fixtures.py:108: in django_db_setup
    **setup_databases_args
venv/lib/python3.6/site-packages/django/test/utils.py:174: in setup_databases
    serialize=connection.settings_dict.get('TEST', {}).get('SERIALIZE', True),
venv/lib/python3.6/site-packages/django/db/backends/base/creation.py:68: in create_test_db
    run_syncdb=True,
venv/lib/python3.6/site-packages/django/core/management/__init__.py:110: in call_command
    command = load_command_class(app_name, command_name)
venv/lib/python3.6/site-packages/django/core/management/__init__.py:36: in load_command_class
    module = import_module('%s.management.commands.%s' % (app_name, name))
/usr/lib/python3.6/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
venv/lib/python3.6/site-packages/django/core/management/commands/migrate.py:14: in <module>
    from django.db.migrations.autodetector import MigrationAutodetector
venv/lib/python3.6/site-packages/django/db/migrations/autodetector.py:11: in <module>
    from django.db.migrations.questioner import MigrationQuestioner
venv/lib/python3.6/site-packages/django/db/migrations/questioner.py:9: in <module>
    from .loader import MigrationLoader
venv/lib/python3.6/site-packages/django/db/migrations/loader.py:8: in <module>
    from django.db.migrations.recorder import MigrationRecorder
venv/lib/python3.6/site-packages/django/db/migrations/recorder.py:9: in <module>
    class MigrationRecorder:
venv/lib/python3.6/site-packages/django/db/migrations/recorder.py:22: in MigrationRecorder
    class Migration(models.Model):
venv/lib/python3.6/site-packages/django/db/models/base.py:101: in __new__
    new_class.add_to_class('_meta', Options(meta, app_label))
venv/lib/python3.6/site-packages/django/db/models/options.py:101: in __init__
    self.db_tablespace = settings.DEFAULT_TABLESPACE
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <dynaconf.base.LazySettings object at 0x7f251735c208>, name = 'DEFAULT_TABLESPACE'

    def __getattr__(self, name):
        """Allow getting keys from self.store using dot notation"""
        if self._wrapped is empty:
            self._setup()
        if name in self._wrapped._deleted:  # noqa
            raise AttributeError(
                f"Attribute {name} was deleted, " "or belongs to different env"
            )

        if name not in RESERVED_ATTRS:
            lowercase_mode = self._kwargs.get(
                "LOWERCASE_READ_FOR_DYNACONF",
                default_settings.LOWERCASE_READ_FOR_DYNACONF,
            )
            if lowercase_mode is True:
                name = name.upper()

        if (
            name.isupper()
            and (
                self._wrapped._fresh
                or name in self._wrapped.FRESH_VARS_FOR_DYNACONF
            )
            and name not in dir(default_settings)
        ):
            return self._wrapped.get_fresh(name)
>       value = getattr(self._wrapped, name)
E       AttributeError: 'Settings' object has no attribute 'DEFAULT_TABLESPACE'

venv/lib/python3.6/site-packages/dynaconf/base.py:164: AttributeError
================================================================================================================================================= short test summary info ==================================================================================================================================================
ERROR app/tests/test_app.py::test_admin_user - AttributeError: 'Settings' object has no attribute 'DEFAULT_TABLESPACE'
===================================================================================================================================================== 1 error in 0.25s =====================================================================================================================================================
```
