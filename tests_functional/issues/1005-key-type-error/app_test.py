"""
https://github.com/dynaconf/dynaconf/issues/1005
"""

from __future__ import annotations

from textwrap import dedent

from dynaconf import Dynaconf


def create_file(fn: str, data: str):
    with open(fn, "w") as file:
        file.write(dedent(data))
    return fn


def test_issue_1005(tmp_path):
    file_a = create_file(
        tmp_path / "t.yaml",
        """\
        default:
          a_mapping:
            1: ["a_string"]
        """,
    )
    create_file(
        tmp_path / "t.local.yaml",
        """\
        default:
          a_value: .inf
        """,
    )

    settings = Dynaconf(settings_file=file_a, merge_enabled=True)

    assert settings.as_dict()["DEFAULT"]["a_mapping"]
    assert settings.as_dict()["DEFAULT"]["a_value"]
