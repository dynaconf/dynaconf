import io
import os
from dynaconf import default_settings
from dynaconf.utils import DynaconfDict
from dynaconf.loaders.py_loader import load


def test_py_loader():
    settings = DynaconfDict(_no_project_root=True)
    with io.open(
        'dummy_module.py', 'w',
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.write('FOO = "bar"')

    load(settings, 'dummy_module')

    os.remove('dummy_module.py')

    load(settings, 'dummy_module.py')
