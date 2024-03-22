"""
[bug] dynaconf 3.2.2 broke dynaconf_include when combined with root_path

https://github.com/dynaconf/dynaconf/issues/1025
"""

from __future__ import annotations

import os
from textwrap import dedent

from dynaconf import Dynaconf


def create_file(name, data):
    with open(name, "w") as file:
        file.write(dedent(data))

    return name


def test_1025(tmp_path):
    os.chdir(tmp_path)
    basedir = tmp_path / "etc"
    basedir.mkdir()
    f1 = create_file(
        basedir / "f1.toml",
        """
        dynaconf_include = [
            "f2.toml",
        ]

        name = "peter"
        """,
    )
    create_file(
        basedir / "f2.toml",
        """
        age = 6
        """,
    )

    settings = Dynaconf(
        settings_file=str(f1.absolute()),
        root_path=basedir.name,
    )
    assert settings.name
    assert settings.age
