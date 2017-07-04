# coding: utf-8

from dynaconf.utils.boxing import DynaBox


box = DynaBox(
    {
        'server': {
            'HOST': 'server.com',
            'port': 8080,
            'PARAMS': {
                'username': 'admin',
                'PASSWORD': 'secret',
                'token': {
                    'TYPE': 1,
                    'value': 2
                }
            }
        }
    },
    box_it_up=True
)


def test_datatypes():
    assert isinstance(box.server, dict)
    assert isinstance(box.server, DynaBox)
    assert isinstance(box.server.host, str)
    assert isinstance(box.server.PORT, int)


def test_access_lowercase():
    assert box.server.host == 'server.com'
    assert box.server.port == 8080
    assert box.server.params.username == 'admin'
    assert box.server.params.password == 'secret'
    assert box.server.params.token.type == 1
    assert box.server.params.token.value == 2


def test_access_uppercase():
    assert box.SERVER.HOST == 'server.com'
    assert box.SERVER.PORT == 8080
    assert box.SERVER.PARAMS.USERNAME == 'admin'
    assert box.SERVER.PARAMS.PASSWORD == 'secret'
    assert box.SERVER.PARAMS.TOKEN.TYPE == 1
    assert box.SERVER.PARAMS.TOKEN.VALUE == 2


def test_access_items():
    assert box['SERVER']['HOST'] == 'server.com'
    assert box['SERVER']['PORT'] == 8080
    assert box['SERVER']['PARAMS']['USERNAME'] == 'admin'
    assert box['SERVER']['PARAMS']['PASSWORD'] == 'secret'
    assert box['SERVER']['PARAMS']['TOKEN']['TYPE'] == 1
    assert box['SERVER']['PARAMS']['TOKEN']['VALUE'] == 2


def test_access_items_lower():
    assert box['server']['HOST'] == 'server.com'
    assert box['server']['PORT'] == 8080
    assert box['server']['params']['USERNAME'] == 'admin'
    assert box['server']['params']['PASSWORD'] == 'secret'
    assert box['server']['params']['TOKEN']['TYPE'] == 1
    assert box['server']['params']['TOKEN']['VALUE'] == 2


def test_get():
    assert box.get('server').get('host') == 'server.com'
    assert box.get('server').get('port') == 8080
    assert box.get('server').get('params').username == 'admin'
    assert box.get('server').get('params').password == 'secret'
    assert box.get('server').get('params').token.type == 1
    assert box.get('server').get('params').token.value == 2
    assert box.get('server').get('blabla') is None
    assert box.get('server').get('blabla', 'foo') == 'foo'
