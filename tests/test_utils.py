# coding: utf-8
import os
import pytest
import tempfile
from dynaconf.utils.parse_conf import unparse_conf_data, parse_conf_data
from dynaconf.utils.files import find_file


def test_unparse():
    """Assert bare types are reversed cast"""
    assert unparse_conf_data('teste') == 'teste'
    assert unparse_conf_data(123) == '@int 123'
    assert unparse_conf_data(123.4) == '@float 123.4'
    assert unparse_conf_data(False) == '@bool False'
    assert unparse_conf_data(True) == '@bool True'
    assert unparse_conf_data(['a', 'b']) == '@json ["a", "b"]'
    assert unparse_conf_data({'name': 'Bruno'}) == '@json {"name": "Bruno"}'
    assert unparse_conf_data(None) == "@none "


def test_cast_bool(settings):
    """Covers https://github.com/rochacbruno/dynaconf/issues/14"""
    assert parse_conf_data(False) is False
    assert settings.get('SIMPLE_BOOL', cast='@bool') is False


def test_find_file():
    """
    Create a temporary folder structure like the following:
        tmpXiWxa5/
        └── child1
            ├── child2
            │   └── child3
            │       └── child4
            └── .env
    Then try to automatically `find_dotenv` starting in `child4`
    """
    tmpdir = os.path.realpath(tempfile.mkdtemp())

    curr_dir = tmpdir
    dirs = []
    for f in ['child1', 'child2', 'child3', 'child4']:
        curr_dir = os.path.join(curr_dir, f)
        dirs.append(curr_dir)
        os.mkdir(curr_dir)

    child1, child4 = dirs[0], dirs[-1]

    # change the working directory for testing
    os.chdir(child4)

    # try without a .env file and force error
    with pytest.raises(IOError):
        find_file(raise_error_if_not_found=True, usecwd=True)

    # try without a .env file and fail silently
    assert find_file(usecwd=True) == ''

    # now place a .env file a few levels up and make sure it's found
    filename = os.path.join(child1, '.env')
    with open(filename, 'w') as f:
        f.write("TEST=test\n")
    assert find_file(usecwd=True) == filename


def test_disable_cast():
    # this casts for int
    assert parse_conf_data('@int 42') == 42
    # now gives pure string
    os.environ['AUTO_CAST_FOR_DYNACONF'] = 'off'
    assert parse_conf_data('@int 42') == '@int 42'
