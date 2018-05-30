import os
import pytest
from pathlib import Path
from click.testing import CliRunner
from dynaconf.cli import main, EXTS, WRITERS, ENVS, read
from dotenv import cli as dotenv_cli


runner = CliRunner()


def run(cmd):
    result = runner.invoke(main, cmd)
    # assert result.exit_code == 0
    return result.output


def test_version():
    assert read('VERSION') in run(['--version'])


def test_help():
    assert 'Dynaconf - Command Line Interface' in run(['--help'])


def test_banner():
    assert 'Learn more at:' in run(['banner'])


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
    assert 'bruno' in open(str(sets)).read()

    if fileformat != 'env':
        os.remove(str(sets))
    else:
        dotenv_cli.unset_key(path, 'NAME')

    if secs_path:
        secs = Path('.secrets.{}'.format(fileformat))
        assert secs.exists() is True
        assert 'TOKEN' in open(str(secs)).read()
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
                '--path={}'.format(str(path)),
                '-y'
            ]
        )

    sets = Path(str(path))
    assert sets.exists() is True
    assert 'value for development' in open(str(sets)).read()

    if secs_path:
        secs = Path(str(secs_path))
        assert secs.exists() is True
        assert 'secret for' in open(str(secs)).read()

    if fileformat != 'env':
        gign = Path(str(tmpdir.join('.gitignore')))
        assert gign.exists() is True
        assert ".secrets.*" in open(str(gign)).read()


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
        assert "TESTVALUE" in open(str(settingspath)).read()
        assert "SECRETVALUE" in open(str(secretfile)).read()
    else:
        assert "Data successful written to {}".format(env_file) in result
        assert "TESTVALUE" in open(str(env_file)).read()
        assert "SECRETVALUE" in open(str(env_file)).read()


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
    assert "TESTVALUE" in open(str(env_file)).read()
    assert "SECRETVALUE" in open(str(env_file)).read()


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

    os.chdir(str(Path(str(toml_valid)).parent))
    result = run(
        [
            'validate',
            '-p',
            str(validation_file)
        ]
    )

    os.chdir(str(Path(str(toml_invalid)).parent))
    result = run(
        [
            'validate',
            '-p',
            str(Path(str(validation_file)).parent)
        ]
    )
    print(result)
