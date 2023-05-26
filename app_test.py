from __future__ import annotations

import os
from pprint import pprint
from textwrap import dedent

import pytest

from dynaconf import Dynaconf
from dynaconf import Validator
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils.inspect import dump_data_by_source
from dynaconf.utils.inspect import inspect_key


def create_file(filename, data):
    """Utility to write files"""
    with open(filename, "w") as f:
        f.write(dedent(data))


@pytest.fixture(scope="function", autouse=True)
def teardown():
    os.environ.clear()


def test_only_settings(tmp_path):
    # setup
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: from_file_a")
    create_file(file_b, "foo: from_file_b")

    setting = Dynaconf(settings_file=[file_a, file_b])

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
    # setup
    os.environ["DYNACONF_FOO"] = "from_envvar"
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    with open(file_a, "w") as f:
        f.write("foo: from_file_a")
    with open(file_b, "w") as f:
        f.write("foo: from_file_b")

    setting = Dynaconf(settings_file=[file_a, file_b])

    source_environ = SourceMetadata("env_global", "unique", "global")
    source_file_a = SourceMetadata("yaml", str(file_a), "default")
    source_file_b = SourceMetadata("yaml", str(file_b), "default")
    assert setting.foo == "from_envvar"
    assert setting._loaded_by_loaders[source_environ] == {"FOO": "from_envvar"}
    assert setting._loaded_by_loaders[source_file_a] == {"FOO": "from_file_a"}
    assert setting._loaded_by_loaders[source_file_b] == {"FOO": "from_file_b"}


def test_only_envvar():
    # setup
    os.environ["DYNACONF_FOO"] = "from_envvar"
    setting = Dynaconf()
    assert setting.foo == "from_envvar"


def test_settings_plus_envvar_with_environments(tmp_path):
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
    assert setting.foo == "from_envvar"


def test_only_validate_default():
    setting = Dynaconf(
        validators=[Validator("foo", default="from_validation_default")]
    )
    assert setting.foo == "from_validation_default"


def test_only_validate_default_with_environment():
    setting = Dynaconf(
        validators=[Validator("foo", default="from_validation_default")],
        environment=True,
    )
    assert setting.foo == "from_validation_default"


def test_validate_default_plus_envvar():
    os.environ["DYNACONF_FOO"] = "from_envvar"
    setting = Dynaconf(
        validators=[Validator("foo", "bar", default="from_validation_default")]
    )
    assert setting.foo == "from_envvar"


def test_only_setting_file_envless_load(tmp_path):
    file_a = tmp_path / "a.yaml"
    create_file(file_a, "foo: from_file_a_DEFAULT")

    setting = Dynaconf(settings_file=file_a)

    assert setting.foo == "from_file_a_DEFAULT"


def test_merging(tmp_path):
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: [1,2]")
    create_file(file_b, "foo: [3,4, dynaconf_merge]")

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    print(setting.foo)
    pprint(setting._loaded_by_loaders)


def test_merging_with_token(tmp_path):
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: [1,2]")
    create_file(file_b, "foo: '@merge [3,4]'\nbar: baz")

    setting = Dynaconf(settings_file=[file_a, file_b])
    dump_data_by_source(setting)
    # source_metadata = SourceMetadata("yaml", file_b, "default", merged=True)
    # assert setting._loaded_by_loaders[source_metadata].merged is True


def test_inspect_key(tmp_path):
    os.environ["DYNACONF_FOO"] = "hello"
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    create_file(file_a, "foo: [1,2]\nbar: asdf")
    create_file(file_b, "foo: 123\nspam: eggs")

    setting = Dynaconf(settings_file=[file_a, file_b])
    print()
    inspect_key(setting, "foo")
    # source_metadata = SourceMetadata("yaml", file_b, "default", merged=True)
    # assert setting._loaded_by_loaders[source_metadata].merged is True
