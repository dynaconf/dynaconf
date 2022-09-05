from __future__ import annotations

from collections import namedtuple

import pytest

from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box import Box
from dynaconf.vendor.box import BoxKeyError
from dynaconf.vendor.box import BoxList


DBDATA = namedtuple("DbData", ["server", "port"])


box = DynaBox(
    {
        "server": {
            "HOST": "server.com",
            "port": 8080,
            "PARAMS": {
                "username": "admin",
                "PASSWORD": "secret",
                "token": {"TYPE": 1, "value": 2},
            },
        },
        "database": DBDATA(server="db.com", port=3306),
    },
)


def test_named_tuple_is_not_transformed():
    """Issue: https://github.com/dynaconf/dynaconf/issues/595"""
    assert isinstance(box.database, DBDATA)
    assert isinstance(box.database, tuple)


def test_datatypes():
    assert isinstance(box.server, dict)
    assert isinstance(box.server, DynaBox)
    assert isinstance(box.server.host, str)
    assert isinstance(box.server.PORT, int)


def test_access_lowercase():
    assert box.server.host == "server.com"
    assert box.server.port == 8080
    assert box.server.params.username == "admin"
    assert box.server.params.password == "secret"
    assert box.server.params.token.type == 1
    assert box.server.params.token.value == 2


def test_access_uppercase():
    assert box.SERVER.HOST == "server.com"
    assert box.SERVER.PORT == 8080
    assert box.SERVER.PARAMS.USERNAME == "admin"
    assert box.SERVER.PARAMS.PASSWORD == "secret"
    assert box.SERVER.PARAMS.TOKEN.TYPE == 1
    assert box.SERVER.PARAMS.TOKEN.VALUE == 2


def test_access_items():
    assert box["SERVER"]["HOST"] == "server.com"
    assert box["SERVER"]["PORT"] == 8080
    assert box["SERVER"]["PARAMS"]["USERNAME"] == "admin"
    assert box["SERVER"]["PARAMS"]["PASSWORD"] == "secret"
    assert box["SERVER"]["PARAMS"]["TOKEN"]["TYPE"] == 1
    assert box["SERVER"]["PARAMS"]["TOKEN"]["VALUE"] == 2


def test_access_items_lower():
    assert box["server"]["HOST"] == "server.com"
    assert box["server"]["PORT"] == 8080
    assert box["server"]["params"]["USERNAME"] == "admin"
    assert box["server"]["params"]["PASSWORD"] == "secret"
    assert box["server"]["params"]["TOKEN"]["TYPE"] == 1
    assert box["server"]["params"]["TOKEN"]["VALUE"] == 2


def test_get():
    assert box.get("server").get("host") == "server.com"
    assert box.get("server").get("port") == 8080
    assert box.get("server").get("params").username == "admin"
    assert box.get("server").get("params").password == "secret"
    assert box.get("server").get("params").token.type == 1
    assert box.get("server").get("params").token.value == 2
    assert box.get("server").get("blabla") is None
    assert box.get("server").get("blabla", "foo") == "foo"


def test_copy_no_cause_inf_recursion():
    box.__copy__()
    box.copy()


def test_accessing_dynabox_inside_boxlist_inside_dynabox():
    data = DynaBox({"nested": [{"deeper": "nest"}]})
    assert data.nested[0].deeper == "nest"
    assert data.NESTED[0].deeper == "nest"
    assert data.NESTED[0].DEEPER == "nest"

    data = DynaBox({"nested": BoxList([DynaBox({"deeper": "nest"})])})
    assert data.nested[0].deeper == "nest"
    assert data.NESTED[0].deeper == "nest"
    assert isinstance(data.NESTED, BoxList)
    assert isinstance(data.NESTED[0], DynaBox)
    assert data.NESTED[0].DEEPER == "nest"
