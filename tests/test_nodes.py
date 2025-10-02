from __future__ import annotations

import copy
from collections import namedtuple

import pytest

from dynaconf.nodes import DataDict
from dynaconf.nodes import DataList
from dynaconf.nodes import DynaconfCore
from dynaconf.nodes import DynaconfNotInitialized
from dynaconf.nodes import get_core
from dynaconf.nodes import init_core
from dynaconf.utils import container_items
from dynaconf.utils import data_print
from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box import BoxList

# DynaBox compatibility tests
# Copied from tests/test_dynabox.py

DBDATA = namedtuple("DbData", ["server", "port"])


ddict = DataDict(
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
    assert isinstance(ddict.database, DBDATA)
    assert isinstance(ddict.database, tuple)


def test_datatypes():
    assert isinstance(ddict.server, dict)
    assert isinstance(ddict.server, DataDict)
    assert isinstance(ddict.server.HOST, str)
    assert isinstance(ddict.server.port, int)


def test_access_lowercase():
    assert ddict.server.host == "server.com"
    assert ddict.server.port == 8080
    assert ddict.server.params.username == "admin"
    assert ddict.server.params.password == "secret"
    assert ddict.server.params.token.type == 1
    assert ddict.server.params.token.value == 2


def test_access_uppercase():
    assert ddict.SERVER.HOST == "server.com"
    assert ddict.SERVER.PORT == 8080
    assert ddict.SERVER.PARAMS.USERNAME == "admin"
    assert ddict.SERVER.PARAMS.PASSWORD == "secret"
    assert ddict.SERVER.PARAMS.TOKEN.TYPE == 1
    assert ddict.SERVER.PARAMS.TOKEN.VALUE == 2


def test_access_items():
    assert ddict["SERVER"]["HOST"] == "server.com"
    assert ddict["SERVER"]["PORT"] == 8080
    assert ddict["SERVER"]["PARAMS"]["USERNAME"] == "admin"
    assert ddict["SERVER"]["PARAMS"]["PASSWORD"] == "secret"
    assert ddict["SERVER"]["PARAMS"]["TOKEN"]["TYPE"] == 1
    assert ddict["SERVER"]["PARAMS"]["TOKEN"]["VALUE"] == 2


def test_access_items_lower():
    assert ddict["server"]["HOST"] == "server.com"
    assert ddict["server"]["PORT"] == 8080
    assert ddict["server"]["params"]["USERNAME"] == "admin"
    assert ddict["server"]["params"]["PASSWORD"] == "secret"
    assert ddict["server"]["params"]["TOKEN"]["TYPE"] == 1
    assert ddict["server"]["params"]["TOKEN"]["VALUE"] == 2


def test_get():
    assert ddict.get("server").get("host") == "server.com"
    assert ddict.get("server").get("port") == 8080
    assert ddict.get("server").get("params").username == "admin"
    assert ddict.get("server").get("params").password == "secret"
    assert ddict.get("server").get("params").token.type == 1
    assert ddict.get("server").get("params").token.value == 2
    assert ddict.get("server").get("blabla") is None
    assert ddict.get("server").get("blabla", "foo") == "foo"


def test_copy_no_cause_inf_recursion():
    ddict.__copy__()
    ddict.copy()


def test_accessing_datadict_inside_datalist_inside_datadict():
    data = DataDict({"nested": [{"deeper": "nest"}]})
    assert data.nested[0].deeper == "nest"
    assert data.NESTED[0].deeper == "nest"
    assert data.NESTED[0].DEEPER == "nest"

    data = DataDict({"nested": DataList([DataDict({"deeper": "nest"})])})
    assert data.nested[0].deeper == "nest"
    assert data.NESTED[0].deeper == "nest"
    assert isinstance(data.NESTED, DataList)
    assert isinstance(data.NESTED[0], DataDict)
    assert data.NESTED[0].DEEPER == "nest"


# Additional Tests


def test_core_initialized():
    core = DynaconfCore("test")

    # Immediate-initialize
    data = DataDict(core=core)
    assert get_core(data) == core

    data = DataDict(box_settings=core)  # compat
    assert get_core(data) == core

    # Post-initialize
    data = DataDict()
    with pytest.raises(DynaconfNotInitialized, match="not initialized"):
        get_core(data)
    init_core(data, core)
    assert get_core(data) == core


data_set = (
    [
        {"a": 1},
        {"a": {"b": 1}},
        {"a": {"b": {"c": 1}}},
        [1],
        [1, [2]],
        [1, [2, [3]]],
        {"a": {"b": [1, {"c": 2}, 3]}},
        [1, [2, {"a": [3]}]],
    ],
)


def test_data_repr():
    data = DataDict({"a": 1, "b": {"c": [1, 2, 3]}})
    print()  # noqa
    print(data)  # noqa
    data_print(data)
    data_print(data, debug=True)


def recursive_walk(container: dict | list, assert_fn):
    """Recursively walk a data tree and run assert_fn on each container."""
    assert_fn(container)
    for k, v in container_items(container):
        if isinstance(v, (dict, list)):
            recursive_walk(v, assert_fn)


@pytest.mark.parametrize("input", data_set)
def test_data_containers_init(input):
    """All the ingested dict/list via init should be converted to DataDict/DataList."""
    DataType = DataDict if isinstance(input, dict) else DataList
    core = DynaconfCore("test")
    data = DataType(input, core=core)

    def assert_fn(container):
        assert container.__class__ in (DataDict, DataList)
        assert get_core(container) == core

    recursive_walk(data, assert_fn)


CAST_ON_INITIALIZATION_ASSUMPTION = """
This assumes the DataDict will recursively transform nested dict/list in
DataDict and Datalist. We may wanna do that, but it breaks behavior.
"""


@pytest.mark.skip(CAST_ON_INITIALIZATION_ASSUMPTION)
def test_dict_methods():
    core = DynaconfCore("test")
    di = DataDict(core=core)

    data0 = {"a": [1, {"b": [2]}]}
    data1 = {"c": [3, {"d": [4]}]}

    def assert_fn(container):
        assert container.__class__ in (DataDict, DataList)
        assert get_core(container) == core

    di["a"] = data0["a"]
    recursive_walk(di, assert_fn)

    di.update(data1)
    recursive_walk(di, assert_fn)

    popped = di.pop("a")
    assert isinstance(popped, DataList)

    d_copy = di.copy()
    assert isinstance(d_copy, DataDict)
    di.clear()
    assert len(di) == 0


@pytest.mark.skip(CAST_ON_INITIALIZATION_ASSUMPTION)
def test_list_methods():
    li = DataList()

    li.append({"x": 1})
    assert isinstance(li[0], DataDict)

    li.extend([{"y": 2}, [1, 2]])
    assert isinstance(li[1], DataDict)
    assert isinstance(li[2], DataList)

    li.insert(0, {"z": 3})
    assert isinstance(li[0], DataDict)

    popped = li.pop()
    assert isinstance(popped, DataList)

    li[1:1] = [{"w": 4}]
    assert isinstance(li[1], DataDict)

    d_copy = li.copy()
    assert isinstance(d_copy, DataList)
    li.clear()
    assert len(li) == 0


def test_nested_structures():
    di = DataDict({"a": [{"x": 1}, {"y": 2}], "b": {"c": [3, 4]}})

    assert isinstance(di["a"], DataList)
    assert isinstance(di["a"][0], DataDict)
    assert isinstance(di["b"], DataDict)
    assert isinstance(di["b"]["c"], DataList)


def test_method_preservation():
    di = DataDict()
    di["a"] = {"x": 1}

    # Dict methods
    assert list(di.keys()) == ["a"]
    assert list(di.values())[0]["x"] == 1
    assert list(di.items())[0][1]["x"] == 1

    li = DataList([1, {"x": 2}])
    # List methods
    assert li.count(1) == 1
    assert li.index({"x": 2}) == 1

    # Sort, reverse
    li = DataList([{"x": 2}, {"x": 1}])
    li.sort(key=lambda x: x["x"])
    assert li[0]["x"] == 1


@pytest.mark.skip(CAST_ON_INITIALIZATION_ASSUMPTION)
def test_mutable_operations():
    di = DataDict()
    # Test setdefault
    item = di.setdefault("a", {"x": 1})
    assert isinstance(item, DataDict)

    # Test dict comprehension conversion
    di = DataDict({k: {"val": v} for k, v in [("a", 1), ("b", 2)]})
    assert all(isinstance(v, DataDict) for v in di.values())
    assert all(isinstance(v, DataDict) for k, v in di.items())

    # Test list concatenation
    li = DataList()
    li += [{"x": 1}]
    assert isinstance(li[0], DataDict)

    # Test multiply
    li = DataList([{"x": 1}]) * 2
    assert isinstance(li[0], DataDict) and isinstance(li[1], DataDict)


def test_repr():
    """Test that no unexpected internal attributes shows up."""
    di = DataDict({"foo": 123})
    dl = DataList([1, 2, 3])
    assert repr(di) == "{'foo': 123}"
    assert repr(dl) == "[1, 2, 3]"


@pytest.fixture
def deprecated_context():
    msg = "is deprecated and will be removed in v4.0"
    with pytest.warns(DeprecationWarning, match=msg):
        yield


class TestBoxCompatibility:
    """Test compatibility with Box library API. Remove in v3.3.0."""

    def test_interface(self):
        data_dict_dir = DataDict().__dir__()
        data_list_dir = DataList().__dir__()
        expected_dynabox_methods = [
            "merge_update",
            "to_dict",
            "to_json",
            "to_yaml",
            "to_toml",
            "from_json",
            "from_yaml",
            "from_toml",
        ]
        expected_box_list_methods = [
            "__copy__",
            "__deepcopy__",
            "to_list",
            "to_json",
            "to_yaml",
            "to_toml",
            "to_csv",
            "from_json",
            "from_yaml",
            "from_toml",
            "from_csv",
        ]

        for method in expected_dynabox_methods:
            assert method in data_dict_dir

        for method in expected_box_list_methods:
            assert method in data_list_dir

    def test_dynabox_merge_update(self, deprecated_context, tmp_path):
        """
        Test that DataDict keeps compatibility with Box public API.
        """
        test_data = {"name": "test", "nested": {"value": 42}}
        data_dict = DataDict(test_data.copy())

        dyna_box = DynaBox(test_data.copy())
        # Test merge_update method works the same
        data_dict.merge_update({"new_key": "new_value"})
        dyna_box.merge_update({"new_key": "new_value"})
        assert data_dict == dyna_box

    def test_dynabox(self, deprecated_context, tmp_path):
        """
        Test that DataDict keeps compatibility with Box public API.
        """
        test_data = {"name": "test", "nested": {"value": 42}}
        data_dict = DataDict(test_data.copy())
        dyna_box = DynaBox(test_data.copy())

        # Test to_yaml, to_json, etc
        contents_of = {}
        for method_name in ("to_dict", "to_json", "to_yaml", "to_toml"):
            datadict_method = getattr(data_dict, method_name)
            dynabox_method = getattr(dyna_box, method_name)
            result = datadict_method()
            assert result == dynabox_method()
            contents_of[method_name] = result

        # Test from_yaml, json, etc
        for method_name_to, content in contents_of.items():
            method_name = method_name_to.replace("to_", "from_")
            if method_name in ("from_dict", "from_toml"):
                # vendored toml breaks with Box too
                continue
            file = tmp_path / method_name.replace("_", ".")
            assert isinstance(content, str)
            file.write_text(content)
            filename = str(file.absolute())
            box_method = getattr(DynaBox, method_name)
            assert box_method(filename=filename) == test_data
            method = getattr(DataDict, method_name)
            assert method(filename=filename) == test_data

    def test_box_list(self, tmp_path, deprecated_context):
        """
        Test that DataList keeps compatibility with BoxList API.
        """
        test_data = [{"name": "item1"}, {"name": "item2"}]
        data_list = DataList(test_data.copy())
        box_list = BoxList(test_data.copy())

        # Test to_yaml, to_json, etc
        contents_of = {}
        for method_name in (
            "to_list",
            "to_json",
            "to_yaml",
            "to_toml",
        ):
            datadict_method = getattr(data_list, method_name)
            boxlist_method = getattr(box_list, method_name)
            result = datadict_method()
            assert result == boxlist_method()
            contents_of[method_name] = result

        # unlike the others, to_csv requires filename...
        box_file = tmp_path / "box.csv"
        box_list.to_csv(str(box_file))
        datalist_file = tmp_path / "datalist.csv"
        data_list.to_csv(str(datalist_file))
        assert box_file.read_text() == datalist_file.read_text()
        contents_of["to_csv"] = datalist_file.read_text()

        # Test from_yaml, json, etc
        for method_name_to, content in contents_of.items():
            method_name = method_name_to.replace("to_", "from_")
            if method_name in ("from_list", "from_toml"):
                # vendored toml breaks with Box too
                continue
            file = tmp_path / method_name.replace("_", ".")
            assert isinstance(content, str)
            file.write_text(content)
            filename = str(file.absolute())
            box_method = getattr(BoxList, method_name)
            assert box_method(filename=filename) == test_data
            method = getattr(DataList, method_name)
            assert method(filename=filename) == test_data

    def test_box_list_copying(self, deprecated_context):
        test_data = [{"a": [1, 2, 3]}, {"a": [4, 5, 6]}]
        datalist_origin = DataList(test_data)
        boxlist_origin = BoxList(test_data)

        datalist_shallow = copy.copy(datalist_origin)
        boxlist_shallow = copy.copy(boxlist_origin)
        assert datalist_shallow == datalist_origin
        assert datalist_shallow is not datalist_origin

        assert boxlist_shallow == boxlist_origin
        assert boxlist_shallow is not boxlist_origin

        data_deep = copy.deepcopy(datalist_origin)
        box_deep = copy.deepcopy(boxlist_origin)
        assert isinstance(data_deep, DataList)
        assert isinstance(box_deep, BoxList)
        assert data_deep == datalist_origin
        assert box_deep == boxlist_origin
        assert data_deep is not datalist_origin
        assert box_deep is not boxlist_origin


class TestCoreFunctions:
    def test_get_core_no_raises(self):
        data = DataDict()

        result = get_core(data, raises=False)
        assert result is None

        core = DynaconfCore("test")
        init_core(data, core)
        result = get_core(data, raises=False)
        assert result == core

    def test_dynaconf_core_constructor(self):
        core_id = "test_core_123"
        core = DynaconfCore(core_id)

        assert core.id == core_id
        assert isinstance(core, DynaconfCore)

    def test_init_core_already_exists(self):
        core1 = DynaconfCore("core1")
        core2 = DynaconfCore("core2")

        data = DataDict(core=core1)
        assert get_core(data) == core1

        init_core(data, core2)
        assert get_core(data) == core1
