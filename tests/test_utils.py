# coding: utf-8
import io
import os
import pytest
import tempfile
from dynaconf import default_settings
from dynaconf.utils import missing, Missing
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
    with io.open(
        filename, 'w',
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.write("TEST=test\n")
    assert find_file(usecwd=True) == filename


def test_disable_cast(monkeypatch):
    # this casts for int
    assert parse_conf_data('@int 42') == 42
    # now gives pure string
    with monkeypatch.context() as m:
        m.setenv('AUTO_CAST_FOR_DYNACONF', 'off')
        assert parse_conf_data('@int 42') == '@int 42'


def test_tomlfy():
    assert parse_conf_data("1", tomlfy=True) == 1
    assert parse_conf_data("true", tomlfy=True) is True
    assert parse_conf_data("'true'", tomlfy=True) == 'true'
    assert parse_conf_data('"42"', tomlfy=True) == "42"
    assert parse_conf_data("[1, 32, 3]", tomlfy=True) == [1, 32, 3]
    assert parse_conf_data("[1.1, 32.1, 3.3]", tomlfy=True) == [1.1, 32.1, 3.3]
    assert parse_conf_data("['a', 'b', 'c']", tomlfy=True) == ['a', 'b', 'c']
    assert parse_conf_data("[true, false]", tomlfy=True) == [True, False]
    assert parse_conf_data("{key='value', v=1}", tomlfy=True
                           ) == {'key': 'value', 'v': 1}


def test_missing_sentinel():

    # The missing singleton should always compare truthfully to itself
    assert missing == missing

    # new instances of Missing should be equal to each other due to
    # explicit __eq__ implmentation check for isinstance.
    assert missing == Missing()

    # The sentinel should not be equal to None, True, or False
    assert missing is not None
    assert missing is not True
    assert missing is not False

    # But the explict typecasting of missing to a bool should evaluate to False
    assert bool(missing) is False

    assert str(missing) == '<dynaconf.missing>'


def test_merge_existing_data():
    obj = {'names': ['bruno', 'karla'], 'data': {'a': 'b'}}

    # merge_unique on list, keep existing items
    merged_unique_names = parse_conf_data(
        data='@merge_unique ["erik", "bruno"]',
        tomlfy=True,
        obj=obj,
        key='names'
    )
    assert merged_unique_names == ['karla', 'erik', 'bruno']

    # merge not unique, duplicate items
    merged_names = parse_conf_data(
        data='@merge ["erik", "bruno"]',
        tomlfy=True,
        obj=obj,
        key='names'
    )
    assert merged_names == ['bruno', 'karla', 'erik', 'bruno']

    merged_data = parse_conf_data(
        data='@merge {b="b1"}',
        tomlfy=True,
        obj=obj,
        key='data'
    )
    assert merged_data == {'b': 'b1', 'a': 'b'}

    with pytest.raises(RuntimeError):
        parse_conf_data(
            data='@merge 123',
            tomlfy=True,
            obj=obj,
            key='data'
        )
