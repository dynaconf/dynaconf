"""
Test dynaconf.utils.inspect:inspect
"""
from __future__ import annotations

import os
from textwrap import dedent

import pytest

from dynaconf import Dynaconf
from dynaconf.utils.inspect import _ensure_serializable
from dynaconf.utils.inspect import get_history
from dynaconf.utils.inspect import inspect_settings
from dynaconf.vendor.ruamel import yaml


@pytest.fixture(autouse=True, scope="function")
def teardown():
    os.environ.clear()


def create_file(filename: str, data: str) -> str:
    with open(filename, "w") as f:
        f.write(dedent(data))
    return filename


default_file_data = """\
foo: from_yaml
dicty:
  a: A
  b:
    - 1
    - c:
      d: D
listy:
  - 1
  - a:
    b: B
    c:
      - 1
      - 2
"""


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


def test_get_history(tmp_path):
    file_a = tmp_path / "a.yml"
    file_b = tmp_path / "b.yml"
    create_file(
        file_a,
        """\
        dicty:
          a: A
          b:
            - 1
            - c:
              d: D
        """,
    )
    create_file(
        file_b,
        """\
        listy:
          - 1
          - a:
            b: B
            c:
              - 1
              - 2
        """,
    )
    settings = Dynaconf(settings_file=[file_a, file_b])
    history = get_history(settings)
    assert len(history) == 2
    # metadata
    assert history[0]["loader"] == "yaml"
    assert history[0]["identifier"] == str(file_a)
    assert history[0]["env"] == "default"
    assert history[1]["loader"] == "yaml"
    assert history[1]["identifier"] == str(file_b)
    assert history[1]["env"] == "default"

    # acessing
    assert history[0]["value"]["DICTY"]["a"] == "A"
    assert history[0]["value"]["DICTY"]["b"][1]["d"] == "D"
    assert history[1]["value"]["LISTY"][0] == 1
    assert history[1]["value"]["LISTY"][1]["c"][0] == 1

    # assert types has been normalized
    assert history[0]["value"]["DICTY"].__class__ == dict
    assert history[1]["value"]["LISTY"].__class__ == list


def test_inspect_print_key(tmp_path, capsys):
    os.environ["DYNACONF_FOO"] = "from_environ"
    os.environ["DYNACONF_BAR"] = "environ_only"
    filename = create_file(tmp_path / "a.yaml", "foo: from_yaml")
    settings = Dynaconf(settings_file=filename)
    inspect_settings(settings, "foo", output_format="yaml")

    stdout, stderr = capsys.readouterr()
    expected = """\
    header:
      current:
        env: main
        key: foo
        value: from_environ
      history_ordering: ascending
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
      current:
        env: main
        key: (all)
        value:
          FOO: from_environ
          BAR: environ_only
      history_ordering: ascending
    """
    assert stdout.startswith(dedent(expected))


def test_inspect_to_file_key(tmp_path, capsys):
    os.environ["DYNACONF_FOO"] = "from_environ"
    os.environ["DYNACONF_BAR"] = "environ_only"
    filename = create_file(tmp_path / "a.yaml", "foo: from_yaml")
    settings = Dynaconf(settings_file=filename)

    file_out = tmp_path / "output.yml"
    inspect_settings(settings, "foo", output_format="yaml", to_file=file_out)

    # open created file
    with open(file_out) as f:
        file_content = yaml.YAML().load(f)

    assert file_content["header"]["current"]["key"] == "foo"
    assert file_content["header"]["current"]["value"] == "from_environ"


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

    assert file_content["header"]["current"]["key"] == "(all)"
    assert file_content["header"]["current"]["value"] == {
        "FOO": "from_environ",
        "BAR": "environ_only",
    }
