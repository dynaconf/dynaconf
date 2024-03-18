"""
Given:
- loaded settings file with three nested levels a.b.c
When
- override nested value (a.b.c) with envvar loading
Should
- access the new value case-insensitive (a.b.c == A.B.C)
Instead
- lowercase override doesn't work, while uppercase work

https://github.com/dynaconf/dynaconf/issues/658
"""

from __future__ import annotations

from textwrap import dedent

from dynaconf import Dynaconf


def create_file(filename: str, data: str):
    """Utility to write files"""
    with open(filename, "w") as f:
        f.write(dedent(data))
    return filename


def new_settings(tmp_path):
    """Common setup for tests"""
    # settings file used
    filename = create_file(
        tmp_path / "s.yaml",
        """\
        a:
          b: foo
          c:
            d: hello
        """,
    )

    # setup
    return Dynaconf(
        envvar_prefix="DYNACONF",
        settings_files=filename,
    )


def test_nested_one_uppercase(monkeypatch, tmp_path):
    monkeypatch.setenv("DYNACONF_A__B", "OK")
    assert new_settings(tmp_path).a.b == "OK"


def test_nested_two_lowercase(monkeypatch, tmp_path):
    monkeypatch.setenv("DYNACONF_a__b__c", "OK")
    assert new_settings(tmp_path).a.b.c == "OK"


def test_nested_two_uppercase(monkeypatch, tmp_path):
    monkeypatch.setenv("DYNACONF_A__B__C", "OK")
    assert new_settings(tmp_path).A.B.C == "OK"
    assert new_settings(tmp_path).a.b.c == "OK"  # failed before
