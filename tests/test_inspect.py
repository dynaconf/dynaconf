"""
Test dynaconf.utils.inspect:inspect
"""
from __future__ import annotations

import os
from textwrap import dedent

import pytest

from dynaconf import Dynaconf
from dynaconf import inspect


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
  A:
    B: c
listy:
  - 1
  - 2
"""


def test_inspect_printing__key(tmp_path):
    os.environ["DYNACONF_FOO"] = "from_environ"
    filename = create_file(tmp_path / "a.yaml", default_file_data)
    settings = Dynaconf(settings_file=filename)
    inspect(settings, "foo")
    inspect(settings, "dicty")


def test_inspect_printing__all():
    pass


def test_inspect_to_file__key():
    pass


def test_inspect_to_file__all():
    pass
