from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from dynaconf import default_settings
from dynaconf import LazySettings
from dynaconf.cli import EXTS
from dynaconf.cli import main
from dynaconf.cli import read_file_in_root_directory
from dynaconf.cli import WRITERS
from dynaconf.utils.files import read_file
from dynaconf.vendor.click.testing import CliRunner


runner = CliRunner()
settings = LazySettings(OPTION_FOR_TESTS=True, environments=True)


def run(cmd, env=None, attr="output"):
    result = runner.invoke(main, cmd, env=env, catch_exceptions=False)
    return getattr(result, attr)


def test_version():
    assert read_file_in_root_directory("VERSION") in run(["--version"])


def test_help():
    assert "Dynaconf - Command Line Interface" in run(["--help"])


def test_banner(clean_env):
    assert "Learn more at:" in run(["--banner"])


def test_init_with_instance_raises(tmpdir):
    result = run(
        [
            "-i",
            "tests.test_cli.settings",
            "init",
            "--env",
            "test",
            f"--path={str(tmpdir)}",
        ]
    )
    assert "-i/--instance option is not allowed for `init` command" in result


def test_init_with_env_warns(tmpdir):
    result = run(["init", "--env", "test", f"--path={str(tmpdir)}"])
    assert "The --env/-e option is deprecated" in result


@pytest.mark.parametrize("fileformat", EXTS)
def test_init_with_path(fileformat, tmpdir):
    # run twice to force load of existing files
    if fileformat == "env":
        path = tmpdir.join(".env")
        secs_path = None
    else:
        path = tmpdir.join(f"settings.{fileformat}")
        secs_path = tmpdir.join(f"/.secrets.{fileformat}")

    for _ in (1, 2):
        run(
            [
                "init",
                f"--format={fileformat}",
                "-v",
                "name=bruno",
                "-s",
                "token=secret for",
                f"--path={str(tmpdir)}",
                "-y",
            ]
        )

    sets = Path(str(path))
    assert sets.exists() is True
    assert "bruno" in read_file(
        str(sets), encoding=default_settings.ENCODING_FOR_DYNACONF
    )

    if secs_path:
        secs = Path(str(secs_path))
        assert secs.exists() is True
        assert "secret for" in read_file(
            str(secs), encoding=default_settings.ENCODING_FOR_DYNACONF
        )

    if fileformat != "env":
        gign = Path(str(tmpdir.join(".gitignore")))
        assert gign.exists() is True
        assert ".secrets.*" in read_file(
            str(gign), encoding=default_settings.ENCODING_FOR_DYNACONF
        )


def test_list(testdir):
    """Test list command shows only user defined vars"""
    result = run(
        ["list"],
        env={
            "ROOT_PATH_FOR_DYNACONF": testdir,
            "INSTANCE_FOR_DYNACONF": "tests.config.settings",
        },
    )
    assert "TEST_KEY<str> 'test_value'" in result


def test_get(testdir):
    """Tests get command"""
    result = run(
        ["get", "TEST_KEY"],
        env={
            "ROOT_PATH_FOR_DYNACONF": testdir,
            "INSTANCE_FOR_DYNACONF": "tests.config.settings",
        },
    )
    assert result == "test_value"


def test_get_json_dict(testdir):
    """Tests get command printing json"""
    env = env = {
        "ROOT_PATH_FOR_DYNACONF": testdir,
        "DYNACONF_DATA__KEY": "value",
        "DYNACONF_DATA__OTHERKEY": "other value",
        "INSTANCE_FOR_DYNACONF": "tests.config.settings",
    }
    result = run(["get", "data"], env=env)
    assert result == '{"KEY": "value", "OTHERKEY": "other value"}'


def test_get_lower(testdir):
    """Tests get command"""
    result = run(
        ["get", "test_key"],
        env={
            "ROOT_PATH_FOR_DYNACONF": testdir,
            "INSTANCE_FOR_DYNACONF": "tests.config.settings",
        },
    )
    assert result == "test_value"


def test_get_unparsed(testdir):
    """Tests get command"""
    result = run(
        ["get", "COMMENTJSON_ENABLED_FOR_DYNACONF", "-u"],
        env={
            "ROOT_PATH_FOR_DYNACONF": testdir,
            "INSTANCE_FOR_DYNACONF": "tests.config.settings",
        },
    )
    assert result == "@bool False"


def test_get_with_default(testdir):
    """Tests get command"""
    result = run(
        ["get", "this_obviously_doesnt_exist_yet", "-d", "Hello123"],
        env={
            "ROOT_PATH_FOR_DYNACONF": testdir,
            "INSTANCE_FOR_DYNACONF": "tests.config.settings",
        },
    )
    assert result == "Hello123"


def test_get_other_env(tmpdir):
    """Tests get command"""
    settings_file = tmpdir.join("settings.json")
    settings_file.write(
        '{"prod": {"name": "admin"}, "development": {"name": "dev"}}'
    )
    instance_file = tmpdir.join("myconfig.py")
    instance_file.write(
        "settings = __import__('dynaconf').Dynaconf("
        f"settings_file=r'{str(settings_file)}',"
        "environments=True"
        ")"
    )

    result = run(
        ["get", "name"],
        env={
            "INSTANCE_FOR_DYNACONF": "myconfig.settings",
        },
    )
    assert result == "dev"

    result = run(
        ["get", "name", "-e", "prod"],
        env={
            "INSTANCE_FOR_DYNACONF": "myconfig.settings",
        },
    )
    assert result == "admin"


def test_help_dont_require_instance(testdir):
    result = os.system("dynaconf list --help")
    assert result == 0


def test_list_export_json(testdir):
    result = run(
        ["-i", "tests.config.settings", "list", "-o", "sets.json"],
        env={"ROOT_PATH_FOR_DYNACONF": testdir},
    )
    assert "TEST_KEY<str> 'test_value'" in result
    assert json.loads(read_file("sets.json"))["TEST_KEY"] == "test_value"


def test_list_with_all(testdir):
    """Test list command with --all includes interval vars"""
    result = run(
        ["-i", "tests.config.settings", "list", "-a"],
        env={"ROOT_PATH_FOR_DYNACONF": testdir},
    )

    assert "TEST_KEY<str> 'test_value'" in result


@pytest.mark.parametrize("loader", WRITERS)
def test_list_with_loader(loader):
    result = run(["-i", "tests.config.settings", "list", "-l", loader])
    assert "Working in main environment" in result


@pytest.mark.parametrize("env", ["default", "development"])
def test_list_with_env(testdir, env):
    result = run(
        ["-i", "tests.config.settingsenv", "list", "-e", env],
        env={"ROOT_PATH_FOR_DYNACONF": testdir},
    )
    assert f"Working in {env} environment" in result


def test_list_with_instance():
    result = run(["-i", "tests.test_cli.settings", "list"])
    assert "OPTION_FOR_TESTS<bool> True" in result


def test_list_with_instance_from_env():
    result = run(
        ["list"], {"INSTANCE_FOR_DYNACONF": "tests.test_cli.settings"}
    )
    assert "OPTION_FOR_TESTS<bool> True" in result


def test_instance_attribute_error():
    result = run(["-i", "tests.test_cli.idontexist", "list"])
    assert "has no attribute 'idontexist'" in result


def test_instance_import_error():
    result = run(["-i", "idontexist.settings", "list"])
    assert "Error: No module named 'idontexist'" in result


def test_instance_pypath_error():
    result = run(["-i", "idontexist", "list"])
    assert "Error: invalid path to settings instance: idontexist" in result


def test_list_with_key():
    result = run(["-i", "tests.config.settings", "list", "-k", "TEST_KEY"])
    assert "TEST_KEY<str> 'test_value'" in result


def test_list_with_invalid_key():
    result = run(["-i", "tests.config.settings", "list", "-k", "TEST_KEY.foo"])
    assert "Key not found" in result


def test_list_with_key_export_json(tmpdir):
    result = run(
        [
            "-i",
            "tests.config.settings",
            "list",
            "-k",
            "TEST_KEY",
            "-o",
            "sets.json",
        ]
    )

    assert "TEST_KEY<str> 'test_value'" in result

    assert "TEST_KEY" in read_file("sets.json")
    assert json.loads(read_file("sets.json"))["TEST_KEY"] == "test_value"
    with pytest.raises(KeyError):
        json.loads(read_file("sets.json"))["ANOTHER_KEY"]


def test_list_with_missing_key():
    result = run(["-i", "tests.config.settings", "list", "-k", "NOTEXISTS"])
    assert "Key not found" in result


@pytest.mark.parametrize("writer", EXTS)
@pytest.mark.parametrize("env", ["default", "development"])
@pytest.mark.parametrize("onlydir", (True, False))
def test_write(writer, env, onlydir, tmpdir):
    if onlydir is True:
        tmpfile = tmpdir
    else:
        tmpfile = tmpdir.join(f"settings.{writer}")

    settingspath = tmpdir.join(f"settings.{writer}")
    secretfile = tmpdir.join(f".secrets.{writer}")
    env_file = tmpdir.join(".env")

    result = run(
        [
            "write",
            writer,
            "-v",
            "TESTVALUE=1",
            "-s",
            "SECRETVALUE=2",
            "-e",
            env,
            "-y",
            "-p",
            str(tmpfile),
        ]
    )
    if writer != "env":
        assert f"Data successful written to {settingspath}" in result
        assert "TESTVALUE" in read_file(
            str(settingspath), encoding=default_settings.ENCODING_FOR_DYNACONF
        )
        assert "SECRETVALUE" in read_file(
            str(secretfile), encoding=default_settings.ENCODING_FOR_DYNACONF
        )
    else:
        assert f"Data successful written to {env_file}" in result
        assert "TESTVALUE" in read_file(
            str(env_file), encoding=default_settings.ENCODING_FOR_DYNACONF
        )
        assert "SECRETVALUE" in read_file(
            str(env_file), encoding=default_settings.ENCODING_FOR_DYNACONF
        )


@pytest.mark.parametrize("path", (".env", "./.env"))
def test_write_dotenv(path, tmpdir):
    env_file = tmpdir.join(path)

    result = run(
        [
            "write",
            "env",
            "-v",
            "TESTVALUE=1",
            "-s",
            "SECRETVALUE=2",
            "-y",
            "-p",
            str(env_file),
        ]
    )

    assert f"Data successful written to {env_file}" in result
    assert "TESTVALUE" in read_file(
        str(env_file), encoding=default_settings.ENCODING_FOR_DYNACONF
    )
    assert "SECRETVALUE" in read_file(
        str(env_file), encoding=default_settings.ENCODING_FOR_DYNACONF
    )


VALIDATION = """
[default]
version = {must_exist=true}
name = {must_exist=true}
password = {must_exist=false}

# invalid rule, must always be a dict
a = 1

  [default.age]
  must_exist = true
  lte = 30
  gte = 10

[production]
project = {eq="hello_world"}
host = {is_not_in=['test.com']}
"""

TOML_VALID = """
[default]
version = "1.0.0"
name = "Dynaconf"
age = 15

[production]
project = "hello_world"
password = 'exists only in prod'
"""

TOML_INVALID = """
[default]
version = "1.0.0"
name = "Dynaconf"
age = 35

[production]
project = "This is not hello_world"
password = 'exists only in prod'
host = "test.com"
"""


def test_validate(tmpdir):
    validation_file = tmpdir.join("dynaconf_validators.toml")
    validation_file.write(VALIDATION)

    toml_valid = tmpdir.mkdir("valid").join("settings.toml")
    toml_valid.write(TOML_VALID)

    toml_invalid = tmpdir.mkdir("invalid").join("settings.toml")
    toml_invalid.write(TOML_INVALID)

    result = run(
        [
            "-i",
            "tests.config.settingsenv",
            "validate",
            "-p",
            str(validation_file),
        ],
        {"SETTINGS_FILE_FOR_DYNACONF": str(toml_valid)},
    )
    assert "Validation success!" in result

    result = run(
        [
            "-i",
            "tests.test_cli.settings",
            "validate",
            "-p",
            str(Path(str(validation_file)).parent),
        ],
        {"SETTINGS_FILE_FOR_DYNACONF": str(toml_invalid)},
    )
    assert "age must lte 30 but it is 35 in env default" in result
    assert (
        "project must eq hello_world but it is This is not hello_world "
        "in env production" in result
    )
    assert (
        "host must is_not_in ['test.com'] but it is test.com in env "
        "production" in result
    )
    assert "Validation success!" not in result
