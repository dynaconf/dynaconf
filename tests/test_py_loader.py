import io
import os
from dynaconf import default_settings
from dynaconf.utils import DynaconfDict
from dynaconf.loaders.py_loader import load


def test_py_loader_form_file(tmpdir):

    settings = DynaconfDict()
    dummy_path = tmpdir.join('dummy_module.py')
    with io.open(
        str(dummy_path), 'w',
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.write('FOO = "bar"')

    load(settings, 'dummy_module.py')
    os.remove('dummy_module.py')
    load(settings, 'dummy_module.py')  # will be ignored not found

    assert settings.get('FOO') == "bar"


def test_py_loader_from_module(tmpdir):

    settings = DynaconfDict()
    dummy_folder = tmpdir.mkdir('dummy')

    dummy_folder.join('dummy_module.py').write('FOO = "bar"')
    dummy_folder.join('__init__.py').write('print("initing dummy...")')

    load(settings, 'dummy.dummy_module')

    assert settings.exists('FOO')
