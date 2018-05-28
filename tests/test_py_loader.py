import os
from dynaconf.utils import DynaconfDict
from dynaconf.loaders.py_loader import load


def test_py_loader():
    settings = DynaconfDict(_no_project_root=True)
    with open('dummy_module.py', 'w') as f:
        f.write('FOO = "bar"')

    load(settings, 'dummy_module')

    os.remove('dummy_module.py')

    load(settings, 'dummy_module.py')
