import io
import os
import pytest
from pathlib import Path
from click.testing import CliRunner
from dynaconf import LazySettings, default_settings
from dynaconf.cli import main, EXTS, WRITERS, ENVS, read_file_in_root_directory
from dotenv import cli as dotenv_cli


runner = CliRunner()


def run(cmd, env=None):
    result = runner.invoke(main, cmd, env=env, catch_exceptions=False)
    # assert result.exit_code == 0
    return result.output


def test_version():
    assert read_file_in_root_directory('VERSION') in run(['--version'])


def test_help():
    assert 'Dynaconf - Command Line Interface' in run(['--help'])


def test_banner():
    assert 'Learn more at:' in run(['--banner'])


@pytest.mark.parametrize("fileformat", EXTS)
def test_init(fileformat):
    if fileformat == 'env':
        path = '.env'
        secs_path = None
    else:
        path = 'settings.{}'.format(fileformat)
        secs_path = '.secrets.{}'.format(fileformat)

    run(
        [
            'init',
            '--no-wg',
            '--format={}'.format(fileformat),
            '-v', 'name=bruno',
            '-s', 'token=secret',
            '-y'
        ]
    )

    sets = Path(path)
    assert sets.exists() is True

    assert 'bruno' in io.open(
        str(sets),
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ).read()

    if fileformat != 'env':
        os.remove(str(sets))
    else:
        dotenv_cli.unset_key(path, 'NAME')

    if secs_path:
        secs = Path('.secrets.{}'.format(fileformat))
        assert secs.exists() is True
        assert 'TOKEN' in io.open(
            str(secs),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()
        os.remove(str(secs))


@pytest.mark.parametrize("fileformat", EXTS)
def test_init_with_path(fileformat, tmpdir):
    # run twice to force load of existing files
    if fileformat == 'env':
        path = tmpdir.join('.env')
        secs_path = None
    else:
        path = tmpdir.join('settings.{}'.format(fileformat))
        secs_path = tmpdir.join('/.secrets.{}'.format(fileformat))

    for _ in (1, 2):
        run(
            [
                'init',
                '--format={}'.format(fileformat),
                '--path={}'.format(str(tmpdir)),
                '-y'
            ],
        )

    sets = Path(str(path))
    assert sets.exists() is True
    assert 'value for development' in io.open(
        str(sets),
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ).read()

    if secs_path:
        secs = Path(str(secs_path))
        assert secs.exists() is True
        assert 'secret for' in io.open(
            str(secs),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()

    if fileformat != 'env':
        gign = Path(str(tmpdir.join('.gitignore')))
        assert gign.exists() is True
        assert ".secrets.*" in io.open(
            str(gign),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()


def test_list():
    result = run(
        [
            'list'
        ]
    )
    assert "DOTENV_STR: 'hello'" in result


@pytest.mark.parametrize("loader", WRITERS)
def test_list_with_loader(loader):
    result = run(
        [
            'list',
            '-l', loader
        ]
    )
    assert "Working in development environment" in result


@pytest.mark.parametrize("env", ENVS)
def test_list_with_env(env):
    result = run(
        [
            'list',
            '-e', env
        ]
    )
    assert "Working in {} environment".format(env) in result


settings = LazySettings(OPTION_FOR_TESTS=True)


def test_list_with_instance():
    result = run(
        [
            '-i', 'tests.test_cli.settings',
            'list',
        ]
    )
    assert "OPTION_FOR_TESTS: True" in result


def test_list_with_instance_from_env(mocker):
    result = run(
        [
            'list',
        ],
        {
            'INSTANCE_FOR_DYNACONF': 'tests.test_cli.settings',
        }
    )
    assert "OPTION_FOR_TESTS: True" in result


def test_instance_attribute_error(mocker):
    result = run(
        [
            '-i', 'tests.test_cli.idontexist',
            'list',
        ]
    )
    assert "module 'tests.test_cli' has no attribute 'idontexist'" in result


def test_instance_import_error(mocker):
    result = run(
        [
            '-i', 'idontexist.settings',
            'list',
        ]
    )
    assert "Error: No module named 'idontexist'" in result


def test_instance_pypath_error(mocker):
    result = run(
        [
            '-i', 'idontexist',
            'list',
        ]
    )
    assert "Error: invalid path to settings instance: idontexist" in result


def test_list_with_key():
    result = run(
        [
            'list',
            '-k', 'DOTENV_STR'
        ]
    )
    assert "DOTENV_STR: 'hello'" in result


def test_list_with_missing_key():
    result = run(
        [
            'list',
            '-k', 'NOTEXISTS'
        ]
    )
    assert "Key not found" in result


@pytest.mark.parametrize("writer", EXTS)
@pytest.mark.parametrize("env", ENVS)
@pytest.mark.parametrize("onlydir", (True, False))
def test_write(writer, env, onlydir, tmpdir):
    if onlydir is True:
        tmpfile = tmpdir
    else:
        tmpfile = tmpdir.join("settings.{}".format(writer))

    settingspath = tmpdir.join("settings.{}".format(writer))
    secretfile = tmpdir.join(".secrets.{}".format(writer))
    env_file = tmpdir.join(".env")

    result = run(
        [
            'write',
            writer,
            '-v', 'TESTVALUE=1',
            '-s', 'SECRETVALUE=2',
            '-e', env,
            '-y',
            '-p', str(tmpfile)
        ]
    )
    if writer != 'env':
        assert "Data successful written to {}".format(settingspath) in result
        assert "TESTVALUE" in io.open(
            str(settingspath),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()
        assert "SECRETVALUE" in io.open(
            str(secretfile),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()
    else:
        assert "Data successful written to {}".format(env_file) in result
        assert "TESTVALUE" in io.open(
            str(env_file),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()
        assert "SECRETVALUE" in io.open(
            str(env_file),
            encoding=default_settings.ENCODING_FOR_DYNACONF
        ).read()


@pytest.mark.parametrize("path", ('.env', './.env'))
def test_write_dotenv(path, tmpdir):
    env_file = tmpdir.join(path)

    result = run(
        [
            'write',
            'env',
            '-v', 'TESTVALUE=1',
            '-s', 'SECRETVALUE=2',
            '-y',
            '-p', str(env_file)
        ]
    )

    assert "Data successful written to {}".format(env_file) in result
    assert "TESTVALUE" in io.open(
        str(env_file),
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ).read()
    assert "SECRETVALUE" in io.open(
        str(env_file),
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ).read()


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
    validation_file = tmpdir.join('dynaconf_validators.toml')
    validation_file.write(VALIDATION)

    toml_valid = tmpdir.mkdir('valid').join('settings.toml')
    toml_valid.write(TOML_VALID)

    toml_invalid = tmpdir.mkdir('invalid').join('settings.toml')
    toml_invalid.write(TOML_INVALID)

    result = run(
        [
            'validate',
            '-p',
            str(validation_file)
        ],
        {
            'SETTINGS_MODULE_FOR_DYNACONF': str(toml_valid),
        }
    )
    assert "Validation success!" in result

    result = run(
        [
            'validate',
            '-p',
            str(Path(str(validation_file)).parent)
        ],
        {
            'SETTINGS_MODULE_FOR_DYNACONF': str(toml_invalid),
        }
    )
    assert "age must lte 30 but it is 35 in env default" in result
    assert "project must eq hello_world but it is This is not hello_world " \
           "in env production" in result
    assert "host must is_not_in ['test.com'] but it is test.com in env " \
           "production" in result
    assert "Validation success!" not in result
