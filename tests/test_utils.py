# coding: utf-8

from dynaconf.utils.parse_conf import unparse_conf_data


def test_unparse():
    assert unparse_conf_data('teste') == 'teste'
    assert unparse_conf_data(123) == '@int 123'
    assert unparse_conf_data(123.4) == '@float 123.4'
    assert unparse_conf_data(False) == '@bool False'
    assert unparse_conf_data(True) == '@bool True'
    assert unparse_conf_data(['a', 'b']) == '@json ["a", "b"]'
    assert unparse_conf_data({'name': 'Bruno'}) == '@json {"name": "Bruno"}'

