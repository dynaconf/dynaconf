"""
Given
- some source is using template substitution '@format {variable}'
- the template and the variable are inside some nested structure
When
- the variable referred to in the template is updated by another source
Should
- execute substitution with the updated/newest value
Instead (before fix)
- the old value (from original source) is used

https://github.com/dynaconf/dynaconf/issues/575
https://github.com/dynaconf/dynaconf/issues/603
https://github.com/dynaconf/dynaconf/issues/690
"""

from __future__ import annotations

import os
from textwrap import dedent
from unittest import mock

import pytest

from dynaconf import Dynaconf


def create_file(filename: str, data: str):
    """Utility to help create tmp files"""
    with open(filename, "w") as f:
        f.write(dedent(data))
    return filename


def test_envvar_override_without_nesting(tmp_path):
    """Works without nesting structures"""
    environ = {"DYNACONF_DB_PORT": "9999"}
    filename = create_file(
        filename=tmp_path / "s.toml",
        data="""\
        DB_PORT='1234'
        DB_ADDRESS='@format 127.0.0.1:{this.db_port}'
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(settings_file=filename)
        assert settings.db_port == 9999  # unwanted casting, but not related
        assert settings.db_address == "127.0.0.1:9999"


def test_envvar_override_with_nesting(tmp_path):
    environ = {"DYNACONF_DATABASE__DB_PORT": "9999"}
    filename = create_file(
        filename=tmp_path / "s.toml",
        data="""\
        [database]
        DB_PORT='1234'
        DB_ADDRESS='@format 127.0.0.1:{this.database.db_port}'
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(settings_file=filename)
        assert settings.database.db_address == "127.0.0.1:9999"


def test_update_method_with_nesting(tmp_path):
    environ = {}
    filename = create_file(
        filename=tmp_path / "s.toml",
        data="""\
        [database]
        DB_PORT='1234'
        DB_ADDRESS='@format 127.0.0.1:{this.database.db_port}'
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(settings_file=filename)
        settings.update({"database": {"db_port": "9999"}}, merge=True)
        assert settings.database.db_port == "9999"
        assert settings.database.db_address == "127.0.0.1:9999"


def test_575_example(tmp_path):
    environ = {"DYNACONF_INGEST__BASE_PATH": "/tmp/ingest"}
    filename = create_file(
        filename=tmp_path / "s.toml",
        data="""\
        INSTALL_DIR = "/opt/myapp"
        LOGS_DIR = "@format {this.INSTALL_DIR}/logs"

        [ingest]
        BASE_PATH = "/opt/ingest"
        LOGS_DIR = "@format {this.ingest.BASE_PATH}/logs"
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(settings_file=filename)
        assert settings.ingest.LOGS_DIR == "/tmp/ingest/logs"
        assert settings.ingest.BASE_PATH == "/tmp/ingest"


def test_690_example(tmp_path):
    environ = {"MYAPP_SERVER__VERSION__RELEASE": "7.2"}
    filename = create_file(
        filename=tmp_path / "s.yaml",
        data="""\
        SERVER:
          VERSION:
            RELEASE: "6.10"
            SNAP: 22
          DEPLOY_WORKFLOW: "deploy-sat-jenkins"
          DEPLOY_ARGUMENTS:
            sat_version: "@format {this.server.version.release}"
            snap_version: "@format {this.server.version.snap}"
            rhel_version: '7'
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(
            envvar_prefix="MYAPP",
            core_loaders=["YAML"],
            settings_file=filename,
        )
        assert settings.server.deploy_arguments.sat_version == "7.2"
        assert settings.server.deploy_arguments.snap_version == "22"
        assert settings.server.deploy_arguments.rhel_version == "7"


def test_666_example(tmp_path):
    environ = {
        "MYAPP_SERVER__VERSION__RELEASE": "7.2",
        "ENV_FOR_DYNACONF": "env1",
    }
    filename = create_file(
        filename=tmp_path / "s.yaml",
        data="""\
        default:
            a_level1:
                prefix: default
                level2:
                    value: "@format {this.a_level1.prefix}-xxx"
            b_level1:
                prefix: default
                level2:
                    some_key: True
                    value: "@format {this.b_level1.prefix}-xxx"
        env1:
            dynaconf_merge: True
            a_level1:
                prefix: env1

            b_level1:
                prefix: env1
                level2:
                    some_key: False
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(settings_file=filename, environments=True)
        assert settings.a_level1.level2.value == "env1-xxx"
        assert settings.b_level1.level2.value == "env1-xxx"


def test_603_example(tmp_path):
    environ = {"DYNACONF_DATABASE__DB_PORT": "9999"}
    filename = create_file(
        filename=tmp_path / "s.toml",
        data="""\
        [default.database]
        DB_HOST = "127.0.0.1"
        DB_PORT = "5432"
        DB_ADDRESS = "@format {this.database.DB_HOST}:{this.database.DB_PORT}"
        """,
    )
    with mock.patch.dict(os.environ, environ):
        settings = Dynaconf(settings_file=filename, environments=True)
        assert settings.database.db_address == "127.0.0.1:9999"
