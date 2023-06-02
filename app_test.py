from __future__ import annotations

import os
from pprint import pprint
from textwrap import dedent

import pytest

from dynaconf import Dynaconf
from dynaconf import Validator
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils.inspect import inspect_settings


def create_file(filename, data):
    """Utility to write files"""
    with open(filename, "w") as f:
        f.write(dedent(data))


@pytest.fixture(scope="function", autouse=True)
def teardown():
    os.environ.clear()


def test_only_settings(tmp_path):
    """Should have correct source/file in SourceMetadata"""
    # setup
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: from_file_a")
    create_file(file_b, "foo: from_file_b")

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_settings(setting, "foo")

    source_metadata_a = SourceMetadata("yaml", str(file_a), "default")
    source_metadata_b = SourceMetadata("yaml", str(file_b), "default")
    assert setting.foo == "from_file_b"
    assert setting._loaded_by_loaders[source_metadata_a] == {
        "FOO": "from_file_a"
    }
    assert setting._loaded_by_loaders[source_metadata_b] == {
        "FOO": "from_file_b"
    }


def test_settings_plus_envvar(tmp_path):
    """Should have correct envvar SourceMetadata"""
    # setup
    os.environ["DYNACONF_FOO"] = "from_envvar"
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    with open(file_a, "w") as f:
        f.write("foo: from_file_a")
    with open(file_b, "w") as f:
        f.write("foo: from_file_b")

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_settings(setting, "foo")

    source_environ = SourceMetadata("env_global", "unique", "global")
    source_file_a = SourceMetadata("yaml", str(file_a), "default")
    source_file_b = SourceMetadata("yaml", str(file_b), "default")
    assert setting.foo == "from_envvar"
    assert setting._loaded_by_loaders[source_environ] == {"FOO": "from_envvar"}
    assert setting._loaded_by_loaders[source_file_a] == {"FOO": "from_file_a"}
    assert setting._loaded_by_loaders[source_file_b] == {"FOO": "from_file_b"}


def test_settings_plus_envvar_with_environments(tmp_path):
    """Should have the expected order"""
    # setup
    os.environ["DYNACONF_FOO"] = "from_envvar"
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(
        file_a,
        """
        default:
          foo: from_file_a_DEFAULT
        development:
          foo: from_file_a_DEV
        """,
    )
    create_file(
        file_b,
        """
        default:
          foo: from_file_b_DEFAULT
        development:
          foo: from_file_b_DEV
        """,
    )

    setting = Dynaconf(settings_file=[file_a, file_b], environments=True)
    print()
    inspect_settings(setting, "foo")

    assert setting.foo == "from_envvar"


def test_only_validate_default():
    setting = Dynaconf(
        validators=[Validator("foo", default="from_validation_default")]
    )
    inspect_settings(setting, "foo")

    assert setting.foo == "from_validation_default"


def test_only_validate_default_with_environment():
    setting = Dynaconf(
        validators=[Validator("foo", default="from_validation_default")],
        environment=True,
    )
    print()
    inspect_settings(setting, "foo")

    assert setting.foo == "from_validation_default"


def test_validate_default_plus_envvar():
    os.environ["DYNACONF_FOO"] = "from_envvar"
    setting = Dynaconf(
        validators=[Validator("foo", "bar", default="from_validation_default")]
    )
    print()
    inspect_settings(setting, "foo")

    assert setting.foo == "from_envvar"


def test_only_setting_file_envless_load(tmp_path):
    file_a = tmp_path / "a.yaml"
    create_file(file_a, "foo: from_file_a_DEFAULT")

    setting = Dynaconf(settings_file=file_a)
    print()
    inspect_settings(setting, "foo")

    assert setting.foo == "from_file_a_DEFAULT"


def test_merging_with_keyword_in_list(tmp_path):
    """SourceMetadata should have merge=True"""
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: [1,2]")
    create_file(file_b, "foo: [3,4, dynaconf_merge]\nbar: baz")

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_settings(setting, "foo")

    source_metadata = SourceMetadata(
        "yaml", str(file_b), "default", merged=True
    )
    assert setting._loaded_by_loaders[source_metadata]


def test_merging_with_keyword_in_dict(tmp_path):
    """SourceMetadata should have merge=True"""
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(
        file_a,
        """\
        foo:
          a: 123
          b: hello
        """,
    )
    create_file(
        file_b,
        """\
        foo:
          a: replaced_by_file_b
          c: new_value
          dynaconf_merge: true
        """,
    )

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_settings(setting, "foo")

    source_metadata = SourceMetadata(
        "yaml", str(file_b), "default", merged=True
    )
    assert setting._loaded_by_loaders[source_metadata]


def test_merging_with_top_file_keywork(tmp_path):
    """SourceMetadata should have merge=True"""
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(
        file_a,
        """\
        foo:
          a: 123
          b: hello
        """,
    )
    create_file(
        file_b,
        """\
        dynaconf_merge: true
        foo:
          a: replaced_by_file_b
          c: new_value
        """,
    )

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_settings(setting, "foo")

    source_metadata = SourceMetadata(
        "yaml", str(file_b), "default", merged=True
    )
    assert setting._loaded_by_loaders[source_metadata]


def test_merging_with_global_config(tmp_path):
    """SourceMetadata should have merge=True"""
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: [1,2]")
    create_file(file_b, "foo: [3,4]\nbar: baz")

    setting = Dynaconf(settings_file=[file_a, file_b], merge_enabled=True)
    print()
    inspect_settings(setting, "foo")

    source_metadata = SourceMetadata(
        "yaml", str(file_b), "default", merged=True
    )
    assert setting._loaded_by_loaders[source_metadata]


def test_merging_with_token(tmp_path):
    """SourceMetadata should have merge=True"""
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: [1,2]")
    create_file(file_b, "foo: '@merge [3,4]'\nbar: baz")

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_settings(setting, "foo")

    source_metadata = SourceMetadata(
        "yaml", str(file_b), "default", merged=True
    )
    assert setting._loaded_by_loaders[source_metadata]


def test_merging_with_token_and_environments(tmp_path):
    """SourceMetadata should have merge=True"""
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(
        file_a,
        """\
        default:
          foo:
            a: from_default_a
        development:
          foo:
            a: 123
            b: hello
        """,
    )
    create_file(
        file_b,
        """\
        default:
          foo:
            a: from_default_b
        development:
          foo:
            dynaconf_merge: true
            a: replaced_by_dev_b
            c: new_value
        """,
    )

    setting = Dynaconf(settings_file=[file_a, file_b], environments=True)
    print()
    inspect_settings(setting, "foo")

    source_metadata = SourceMetadata(
        "yaml", str(file_b), "development", merged=True
    )
    assert setting._loaded_by_loaders[source_metadata]
