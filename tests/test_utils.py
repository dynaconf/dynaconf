# coding: utf-8

from dynaconf.utils.parse_conf import unparse_conf_data, parse_conf_data


def test_unparse():
    """Assert bare types are reversed cast"""
    assert unparse_conf_data('teste') == 'teste'
    assert unparse_conf_data(123) == '@int 123'
    assert unparse_conf_data(123.4) == '@float 123.4'
    assert unparse_conf_data(False) == '@bool False'
    assert unparse_conf_data(True) == '@bool True'
    assert unparse_conf_data(['a', 'b']) == '@json ["a", "b"]'
    assert unparse_conf_data({'name': 'Bruno'}) == '@json {"name": "Bruno"}'


def test_cast_bool(settings):
    """Covers https://github.com/rochacbruno/dynaconf/issues/14"""
    assert parse_conf_data(False) is False
    assert settings.get('SIMPLE_BOOL', cast='@bool') is False
