import os
from pprint import pprint
from textwrap import dedent

from dynaconf import Dynaconf, Validator
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils.inspect import dump_data_by_source


def test_only_settings(tmp_path):
    # setup
    file_a = tmp_path / "a.yaml"
    file_b = tmp_path / "b.yaml"
    with open(file_a, "w") as f:
        f.write("foo: from_file_a")
    with open(file_b, "w") as f:
        f.write("foo: from_file_b")

    setting = Dynaconf(settings_file=[file_a, file_b])
    dump_data_by_source(setting)
    assert setting.foo == "from_file_b"


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
    dump_data_by_source(setting)
    assert setting.foo == "from_envvar"
    assert setting.loaded_by_loaders[SourceMetadata("yaml", str(file_a), "default")]
    assert setting.loaded_by_loaders[SourceMetadata("yaml", str(file_b), "default")]


def create_file(filename, data):
    """Utility to write files"""
    with open(filename, "w") as f:
        f.write(dedent(data))


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
    setting = Dynaconf(validators=[Validator("foo", default="from_validation_default")])
    print()
    print(setting.loaded_by_loaders)
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

    setting = Dynaconf(
        settings_file=file_a,
    )

    print()
    print(setting.loaded_by_loaders)
    assert setting.foo == "from_file_a_DEFAULT"
    # assert setting.loaded_by_loaders[("yaml", str(file_a), "default")]
