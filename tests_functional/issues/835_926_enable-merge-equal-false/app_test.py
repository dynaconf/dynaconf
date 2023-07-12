from textwrap import dedent

import pytest

from dynaconf import Dynaconf
from dynaconf.utils.inspect import get_history


def create_file(filename: str, data: str) -> str:
    """Utility to create files"""
    with open(filename, "w") as file:
        file.write(dedent(data))
    return filename


def test_case_835(tmp_path):
    """
    When using dynaconf_merge=False inside a structure
    Should prevent merging of that structure
    """
    file_a = create_file(
        tmp_path / "a.toml",
        """\
        [general]
        a = 1

        [other]
        a = 2
        """,
    )

    file_b = create_file(
        tmp_path / "b.toml",
        """\
        [general]
        b = 1

        [other]
        dynaconf_merge = false
        b = 2
        """,
    )
    settings = Dynaconf(
        settings_files=[file_a, file_b],
        merge_enabled=True,
    )

    assert settings.other.b == 2
    with pytest.raises(AttributeError):
        settings.other.a


def test_case_926_workaround(tmp_path):
    """
    The original example is not a bug because toplevel always merges.
    But it can be achieved by explicitly deleting old keys.
    """
    file_a = create_file(
        tmp_path / "a.toml",
        """\
        [default]
        DEBUG = true
        [default.nested]
        Name="Test"
        """,
    )

    file_hooks = create_file(
        tmp_path / "dynaconf_hooks.py",
        """\
        def post(settings):
            data = {}
            if settings.DEBUG:
                data["database_url"] = "sqlite://"
                data["name"] = "@del"
            return data
        """,
    )
    settings = Dynaconf(
        environments=True,
        settings_files=[file_a, file_hooks],
    )

    assert settings.database_url == "sqlite://"
    with pytest.raises(AttributeError):
        settings.name


def test_case_926_local_scope_merge_marks(tmp_path):
    """
    When using merge=False on inner structure with global merge_enabled=True
    Should prevent merging from that level (in dicts)
    """
    file_a = create_file(
        tmp_path / "a.toml",
        """\
        [default]
        DEBUG = true
        [default.nested]
        Name="Test"
        """,
    )

    file_hooks = create_file(
        tmp_path / "dynaconf_hooks.py",
        """\
        def post(settings):
            data = {}
            if settings.DEBUG:
                data["nested"] = {
                    "database_url": "sqlite://",
                    "dynaconf_merge": False
                }
            return data
        """,
    )
    settings = Dynaconf(
        environments=True,
        settings_files=[file_a, file_hooks],
    )

    assert settings.nested.database_url == "sqlite://"
    with pytest.raises(AttributeError):
        settings.nested.name


def test_case_926_file_scope_merge_mark(tmp_path):
    """
    When using merge=False on toplevel with global merge_enabled=True
    Should propagate merge=False to nested structures
    """
    file_a = create_file(
        tmp_path / "a.toml",
        """\
        [default]
        DEBUG = true
        [default.nested]
        Name="Test"
        """,
    )

    file_hooks = create_file(
        tmp_path / "dynaconf_hooks.py",
        """\
        def post(settings):
            data = {"dynaconf_merge": False}
            if settings.DEBUG:
                data["nested"] = {"database_url": "sqlite://"}
            return data
        """,
    )
    settings = Dynaconf(
        environments=True,
        settings_files=[file_a, file_hooks],
    )

    assert settings.nested.database_url == "sqlite://"
    with pytest.raises(AttributeError):
        settings.nested.name


def test_local_scope_merge_false():
    """ """
    settings = Dynaconf(
        environments=True,
        merge_enabled=True,
    )
    settings.set("dicty.name", "foo")
    settings.set("listy", [1, 2, 3])
    settings.update({"dicty": {"database_url": "sqlite://", "dynaconf_merge": False}})
    settings.update({"listy": [9999]})

    assert settings.dicty == {"database_url": "sqlite://"}
    assert settings.listy == [1, 2, 3, 9999]


def test_file_scope_merge_false(tmp_path):
    """
    Similar to when using a merge_enabled=true in the toplevel of a file,
    using merge_enabled=false should prevent all structures of that scope from
    merging (with the exception of the toplevel itself), even if global
    merge_enabled=True.
    """
    # file-scope dynaconf_merge=True, merge_enabled=False
    file_a = create_file(
        tmp_path / "a.toml",
        """\
        dicty={name="foo"}
        listy=[1, 2, 3]
        """,
    )
    file_b = create_file(
        tmp_path / "b.toml",
        """\
        dynaconf_merge=true
        dicty={database_url="sqlite://"}
        listy=[9999]
        """,
    )
    settings = Dynaconf(merge_enabled=False, settings_file=[file_a, file_b])
    assert settings.dicty == {"database_url": "sqlite://", "name": "foo"}
    assert settings.listy == [1, 2, 3, 9999]

    # file-scope dynaconf_merge=False, merge_enabled=True
    file_c = create_file(
        tmp_path / "c.toml",
        """\
        dicty={name="foo"}
        listy=[1, 2, 3]
        """,
    )
    file_d = create_file(
        tmp_path / "d.toml",
        """\
        dynaconf_merge=false
        dicty={database_url="sqlite://"}
        listy=[9999]
        """,
    )
    settings = Dynaconf(merge_enabled=True, settings_file=[file_c, file_d])
    assert settings.dicty == {"database_url": "sqlite://"}
    assert settings.listy == [9999]


def test_regression_expected_merge_on_toplevel_structure(tmp_path):
    """
    Top-level merges are implicitly always True.
    It is expected that the merge_enabled flag and local merge marks don't
    take effect on the top-level/root structure.
    """
    file_a = create_file(
        tmp_path / "a.toml",
        """\
        [default]
        from_a="foo"
        """,
    )

    file_b = create_file(
        tmp_path / "b.toml",
        """\
        [default]
        from_b="bar"
        """,
    )

    settings = Dynaconf(
        environments=True, settings_files=[file_a, file_b], merge_enabled=False
    )

    assert settings.from_a == "foo"
    assert settings.from_b == "bar"


def test_regression_global_set_merge():
    settings = Dynaconf()
    settings.set("MERGE_ENABLED_FOR_DYNACONF", True)
    settings.set("MERGE_KEY", {"items": [{"name": "item 1"}, {"name": "item 2"}]})
    settings.set("MERGE_KEY", {"items": [{"name": "item 3"}, {"name": "item 4"}]})
    assert settings.MERGE_KEY == {
        "items": [
            {"name": "item 1"},
            {"name": "item 2"},
            {"name": "item 3"},
            {"name": "item 4"},
        ]
    }


def test_regression_local_set_merge():
    settings = Dynaconf()
    settings.set("DATABASE", {"host": "localhost", "port": 666})
    settings.set("DATABASE", {"host": "localhost", "port": 666})
    assert settings.DATABASE == {"host": "localhost", "port": 666}

    settings.set("DATABASE", {"host": "new", "user": "admin", "dynaconf_merge": True})
    assert settings.DATABASE == {"host": "new", "port": 666, "user": "admin"}
    assert settings.DATABASE.HOST == "new"
    assert settings.DATABASE.user == "admin"


def test_regression_dotted_merge_should_be_false_1(tmp_path):
    filename = create_file(
        tmp_path / "t.toml",
        """\
        [default]
        foo='from_env_default'
        [development]
        foo='from_env_development'
        [prod]
        bar='prod_only'
        spam='should_appear'
        """,
    )
    settings = Dynaconf(settings_file=filename, environments=True)
    settings.from_env("prod")
    history = get_history(settings)
    for record in history:
        assert record["merged"] is False


def test_regression_dotted_merge_should_be_false_2(tmp_path):
    filename = create_file(
        tmp_path / "t.toml",
        """\
        default.foo='from_env_default'
        development.foo='from_env_development'
        prod.bar='prod_only'
        prod.spam='should_appear'
        """,
    )
    settings = Dynaconf(settings_file=filename, environments=True)
    settings.from_env("prod")
    history = get_history(settings)
    for record in history:
        assert record["merged"] is False


def test_regression_include(tmp_path):
    include_file = create_file(
        tmp_path / "foo.toml",
        f"""\
        [default]
        key_b="bar"
        dicty={{spam_b="eggs_b"}}
        listy=[999]
        """,
    )
    file_a = create_file(
        tmp_path / "t.toml",
        f"""\
        [default]
        key_a="foo"
        dicty={{spam_a="eggs_a"}}
        listy=[1,2,3]
        dynaconf_include="{include_file}"
        """,
    )
    settings = Dynaconf(settings_file=file_a, environments=True, merge_enabled=True)
    assert settings.dicty.spam_a == "eggs_a"
    assert settings.dicty.spam_b == "eggs_b"
    assert settings.listy == [1,2,3,999]
    assert settings.key_a == "foo"
    assert settings.key_b == "bar"
