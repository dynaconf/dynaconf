"""
Test dynaconf.utils.inspect:inspect
"""
from __future__ import annotations

import copy
import os
from pprint import pprint
from textwrap import dedent
from unittest import mock

import pytest

from dynaconf import Dynaconf
from dynaconf.utils.inspect import _ensure_serializable
from dynaconf.utils.inspect import get_history
from dynaconf.utils.inspect import inspect_settings
from dynaconf.validator import Validator
from dynaconf.vendor.ruamel import yaml


def create_file(filename: str, data: str) -> str:
    with open(filename, "w") as f:
        f.write(dedent(data))
    return filename


def is_dict_subset(original: dict, partial: dict) -> bool:
    """Check if partial dict is subset of original dict."""
    return {**original, **partial} == original


@pytest.fixture(autouse=True, scope="function")
def teardown():
    backup = copy.deepcopy(os.environ)
    for key in os.environ.keys():
        if key.startswith(("DYNACONF_", "FLASK_", "DJANGO_")):
            del os.environ[key]
    yield
    os.environ.update(backup)


@pytest.fixture(autouse=True, scope="module")
def module_teardown():
    yield
    for key in os.environ.keys():
        if key.startswith(("DYNACONF_", "FLASK_", "DJANGO_")):
            del os.environ[key]


def test_ensure_serializable():
    settings = Dynaconf()
    settings.update(
        {
            "listy": [1, 2, 3, {"a": "A", "b": [4, 5, 6]}],
            "dicty": {"a": "A", "b": [1, 2, 3, {"a": "A", "b": "B"}]},
        }
    )
    normal_list = _ensure_serializable(settings.listy)
    normal_dict = _ensure_serializable(settings.dicty)
    assert normal_list.__class__ == list
    assert normal_list[3].__class__ == dict
    assert normal_list[3]["b"].__class__ == list

    assert normal_dict.__class__ == dict
    assert normal_dict["b"].__class__ == list  # type: ignore
    assert normal_dict["b"][3].__class__ == dict  # type: ignore


def test_get_history_general(tmp_path):
    """
    Given two yaml files
    Should return
        - list of length 2
        - per-file metadata containing: loader, identifier, env and value.
        - correct types: dicts and lists, not DynaBox and BoxList
    """
    file_a = tmp_path / "a.yml"
    file_b = tmp_path / "b.yml"
    create_file(
        file_a,
        """\
        dicty:
          a: A
          b:
            - 1
            - c: C
              d: D
        """,
    )
    create_file(
        file_b,
        """\
        listy:
          - 1
          - a: A
            b: B
            c:
              - 1
              - 2
        """,
    )
    settings = Dynaconf(settings_file=[file_a, file_b])
    history = get_history(settings)

    # metadata
    assert len(history) == 2
    assert is_dict_subset(
        history[0],
        {
            "loader": "yaml",
            "identifier": str(file_a),
            "env": "default",
            "merged": False,
        },
    )
    assert is_dict_subset(
        history[1],
        {
            "loader": "yaml",
            "identifier": str(file_b),
            "env": "default",
            "merged": False,
        },
    )

    # data integrity
    assert history[0]["value"]["DICTY"] == {
        "a": "A",
        "b": [1, {"c": "C", "d": "D"}],
    }
    assert history[1]["value"]["LISTY"] == [
        1,
        {"a": "A", "b": "B", "c": [1, 2]},
    ]

    # types has been normalized
    assert history[0]["value"]["DICTY"].__class__ == dict
    assert history[1]["value"]["LISTY"].__class__ == list


def test_get_history_env_false__file_plus_envvar(tmp_path):
    """
    Given environments=False and sources=file+envvar
    Should return correct metadata history
    """
    os.environ["DYNACONF_FOO"] = "from_environ"
    file_a = tmp_path / "a.yml"
    create_file(file_a, "foo: from_file")

    settings = Dynaconf(settings_file=file_a)
    history = get_history(settings)

    # metadata
    assert len(history) == 2
    assert is_dict_subset(
        history[0],
        {
            "loader": "yaml",
            "identifier": str(file_a),
            "env": "default",
            "merged": False,
        },
    )
    assert is_dict_subset(
        history[1],
        {
            "loader": "env_global",
            "identifier": "unique",
            "env": "global",
            "merged": False,
        },
    )


def test_get_history_env_false__val_default_plus_envvar():
    """
    Given environments=False and sources=validation-default+envvar
    Should return correct metadata history
    """
    os.environ["DYNACONF_FOO"] = "from_environ"

    settings = Dynaconf(
        validators=[Validator("bar", default="from_val_default")]
    )
    history = get_history(settings)

    # metadata (validation_default runs after envvar loading)
    assert len(history) == 2
    assert is_dict_subset(
        history[0],
        {
            "loader": "env_global",
            "identifier": "unique",
            "env": "global",
            "merged": False,
        },
    )
    assert is_dict_subset(
        history[1],
        {
            "loader": "validation_default",
            "identifier": "unique",
            "env": "main",
            "merged": False,
        },
    )


def test_get_history_env_false__merge_marks(tmp_path):
    """
    Given environments=False and sources=envvar+file
    Should return correct metadata history
    """
    os.environ["DYNACONF_LISTY"] = "@merge [10,11,12]"
    file_a = tmp_path / "file_a.toml"
    file_b = tmp_path / "file_b.toml"
    file_c = tmp_path / "file_c.toml"
    create_file(file_a, "listy=[1,2,3]")
    create_file(file_b, "listy=[4,5,6, 'dynaconf_merge']")
    create_file(file_c, "dynaconf_merge=true\nlisty=[7,8,9]")

    settings = Dynaconf(settings_file=[file_a, file_b, file_c])
    history = get_history(settings)

    # metadata
    assert len(history) == 4
    assert history[0] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "default",
        "merged": False,
        "value": {"LISTY": [1, 2, 3]},
    }
    assert history[1] == {
        "loader": "toml",
        "identifier": str(file_b),
        "env": "default",
        "merged": True,
        "value": {"LISTY": [1, 2, 3, 4, 5, 6]},
    }
    assert history[2] == {
        "loader": "toml",
        "identifier": str(file_c),
        "env": "default",
        "merged": True,
        "value": {"LISTY": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    }
    assert history[3] == {
        "loader": "env_global",
        "identifier": "unique",
        "env": "global",
        "merged": True,
        "value": {"LISTY": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
    }


def test_get_history_env_true__file_plus_envvar(tmp_path):
    """
    Given environments=True and sources=file+envvar
    Should return correct metadata history
    """
    os.environ["DYNACONF_FOO"] = "from_environ"
    file_a = tmp_path / "a.toml"
    create_file(
        file_a,
        """\n
        default.foo="from_default_env"
        development.foo="from_development_env"
        """,
    )

    settings = Dynaconf(settings_file=file_a, environments=True)
    history = get_history(settings)

    assert len(history) == 3
    assert history[0] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "default",
        "merged": False,
        "value": {"FOO": "from_default_env"},
    }
    assert history[1] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "development",
        "merged": False,
        "value": {"FOO": "from_development_env"},
    }
    assert history[2] == {
        "loader": "env_global",
        "identifier": "unique",
        "env": "global",
        "merged": False,
        "value": {"FOO": "from_environ"},
    }


def test_get_history_env_true__val_default_plus_file(tmp_path):
    """
    Given environments=True and sources=validation-default+file
    Should return correct metadata history
    """
    file_a = tmp_path / "a.toml"
    create_file(
        file_a,
        """\
        default.foo="from_default_file"
        development.foo="from_development_file"
        """,
    )
    print()
    settings = Dynaconf(
        validators=[
            Validator("bar", default="from_val_default_current_env"),
            Validator(
                "baz", env="production", default="from_val_default_prod"
            ),
        ],
        settings_file=file_a,
        environments=True,
    )
    history = get_history(settings)

    assert len(history) == 4
    assert history[0] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "default",
        "merged": False,
        "value": {"FOO": "from_default_file"},
    }
    assert history[1] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "development",
        "merged": False,
        "value": {"FOO": "from_development_file"},
    }
    assert history[2] == {
        "loader": "validation_default",
        "identifier": "unique",
        "env": "development",
        "merged": False,
        "value": {"BAR": "from_val_default_current_env"},
    }
    assert history[3] == {
        "loader": "validation_default",
        "identifier": "unique",
        "env": "production",
        "merged": False,
        "value": {"BAZ": "from_val_default_prod"},
    }


def test_get_history_env_true__merge_marks(tmp_path):
    """
    Given environments=True and sources=envvar+file
    Should return correct metadata history
    """
    os.environ["DYNACONF_LISTY"] = "@merge [10,11,12]"
    file_a = tmp_path / "file_a.toml"
    file_b = tmp_path / "file_b.toml"
    file_c = tmp_path / "file_c.toml"
    create_file(file_a, "listy=[1,2,3]")
    create_file(file_b, "listy=[4,5,6, 'dynaconf_merge']")
    create_file(file_c, "dynaconf_merge=true\nlisty=[7,8,9]")

    settings = Dynaconf(settings_file=[file_a, file_b, file_c])
    history = get_history(settings)

    # metadata
    assert len(history) == 4
    assert history[0] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "default",
        "merged": False,
        "value": {"LISTY": [1, 2, 3]},
    }
    assert history[1] == {
        "loader": "toml",
        "identifier": str(file_b),
        "env": "default",
        "merged": True,
        "value": {"LISTY": [1, 2, 3, 4, 5, 6]},
    }
    assert history[2] == {
        "loader": "toml",
        "identifier": str(file_c),
        "env": "default",
        "merged": True,
        "value": {"LISTY": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    }
    assert history[3] == {
        "loader": "env_global",
        "identifier": "unique",
        "env": "global",
        "merged": True,
        "value": {"LISTY": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
    }


def test_inspect_print_key(tmp_path, capsys):
    os.environ["DYNACONF_FOO"] = "from_environ"
    os.environ["DYNACONF_BAR"] = "environ_only"
    filename = create_file(tmp_path / "a.yaml", "foo: from_yaml")
    settings = Dynaconf(settings_file=filename)
    inspect_settings(settings, "foo", output_format="yaml")

    stdout, stderr = capsys.readouterr()
    expected = """\
    header:
      filters:
        env: None
        key: foo
        history_ordering: ascending
      active_value: from_environ
    """
    assert stdout.startswith(dedent(expected))


def test_inspect_print_all(tmp_path, capsys):
    os.environ["DYNACONF_FOO"] = "from_environ"
    os.environ["DYNACONF_BAR"] = "environ_only"
    filename = create_file(tmp_path / "a.yaml", "foo: from_yaml")
    settings = Dynaconf(settings_file=filename)
    inspect_settings(settings, output_format="yaml")

    stdout, stderr = capsys.readouterr()
    expected = """\
    header:
      filters:
        env: None
        key: None
        history_ordering: ascending
      active_value:
        FOO: from_environ
        BAR: environ_only
    """
    assert stdout.startswith(dedent(expected))


def test_inspect_to_file_key(tmp_path):
    os.environ["DYNACONF_FOO"] = "from_environ"
    os.environ["DYNACONF_BAR"] = "environ_only"
    filename = create_file(tmp_path / "a.yaml", "foo: from_yaml")
    settings = Dynaconf(settings_file=filename)

    file_out = tmp_path / "output.yml"
    inspect_settings(settings, "foo", output_format="yaml", to_file=file_out)

    # open created file
    with open(file_out) as f:
        file_content = yaml.YAML().load(f)

    assert file_content["header"]["filters"]["key"] == "foo"
    assert file_content["header"]["active_value"] == "from_environ"


def test_inspect_to_file_all(tmp_path):
    os.environ["DYNACONF_FOO"] = "from_environ"
    os.environ["DYNACONF_BAR"] = "environ_only"
    filename = create_file(tmp_path / "a.yaml", "foo: from_yaml")
    settings = Dynaconf(settings_file=filename)

    file_out = tmp_path / "output.yml"
    inspect_settings(settings, output_format="yaml", to_file=file_out)

    # open created file
    with open(file_out) as f:
        file_content = yaml.YAML().load(f)

    assert file_content["header"]["filters"]["key"] == "None"
    assert file_content["header"]["active_value"] == {
        "FOO": "from_environ",
        "BAR": "environ_only",
    }


def test_inspect_env_filter(tmp_path, capsys):
    """
    Caveat: env filter will show current default env values too.
            History will be filtered properly.
    """
    filename = create_file(
        tmp_path / "a.toml",
        """\
        default.foo="from_env_default"
        development.foo="from_env_dev"
        prod.bar="prod_only"
        """,
    )

    settings = Dynaconf(settings_file=filename, environments=True)

    inspect_settings(settings, output_format="yaml", env="prod")
    stdout, stderr = capsys.readouterr()
    expected = """\
    header:
      filters:
        env: prod
        key: None
        history_ordering: ascending
      active_value:
        FOO: from_env_default
        BAR: prod_only
    """
    assert stdout.startswith(dedent(expected))


def test_caveat__get_history_env_true(tmp_path):
    """
    Given environments=True and sources=file
    Should return correct metadata history

    Caveat:
        An environment that is not a builtin env name, like (default,
        global, development) and that is not the 'current_env' will not
        be loaded and, thus, will not be shown in history.

        Possible workaround:
        a) leave for the user to trigger this env loaded.
           >>> settings.from_env("production")
        b) add a global config for loading all envs, even if they are
           not in the builtin env names.
    """
    file_a = tmp_path / "a.toml"
    create_file(
        file_a,
        """\n
        default.foo="from_default_env"
        development.foo="from_development_env"
        production.foo="from_production_env"
        """,
    )

    settings = Dynaconf(settings_file=file_a, environments=True)
    history = get_history(settings)

    assert len(history) == 2
    assert history[0] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "default",
        "merged": False,
        "value": {"FOO": "from_default_env"},
    }
    assert history[1] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "development",
        "merged": False,
        "value": {"FOO": "from_development_env"},
    }

    with pytest.raises(IndexError):
        assert history[2] == {
            "loader": "toml",
            "identifier": str(file_a),
            "env": "production",
            "merged": False,
            "value": {"FOO": "from_production_env"},
        }


def test_caveat__get_history_env_true_workaround(tmp_path):
    """
    Given environments=True and sources=file
    Should return correct metadata history

    Caveat: see original test
    Workaround: force loading with desired 'current_env'
    """
    file_a = tmp_path / "a.toml"
    create_file(
        file_a,
        """\n
        default.foo="from_default_env"
        development.foo="from_development_env"
        production.foo="from_production_env"
        """,
    )

    settings = Dynaconf(settings_file=file_a, environments=True)
    settings.from_env("production")
    history = get_history(settings)

    assert len(history) == 3
    assert history[0] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "default",
        "merged": False,
        "value": {"FOO": "from_default_env"},
    }
    assert history[1] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "development",
        "merged": False,
        "value": {"FOO": "from_development_env"},
    }

    assert history[2] == {
        "loader": "toml",
        "identifier": str(file_a),
        "env": "production",
        "merged": False,
        "value": {"FOO": "from_production_env"},
    }
