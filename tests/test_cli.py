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
    assert 'bruno' in open(sets).read()

    if fileformat != 'env':
        os.remove(sets)
    else:
        dotenv_cli.unset_key(path, 'NAME')

    if secs_path:
        secs = Path('.secrets.{}'.format(fileformat))
        assert secs.exists() is True
        assert 'TOKEN' in open(secs).read()
        os.remove(secs)


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

    sets = Path(path)
    assert sets.exists() is True
    assert 'value for development' in open(sets).read()

    if secs_path:
        secs = Path(secs_path)
        assert secs.exists() is True
        assert 'secret for' in open(secs).read()

    if fileformat != 'env':
        gign = Path(tmpdir.join('.gitignore'))
        assert gign.exists() is True
        assert ".secrets.*" in open(gign).read()


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
        assert "TESTVALUE" in open(settingspath).read()
        assert "SECRETVALUE" in open(secretfile).read()
    else:
        assert "Data successful written to {}".format(env_file) in result
        assert "TESTVALUE" in open(env_file).read()
        assert "SECRETVALUE" in open(env_file).read()


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
    assert "TESTVALUE" in open(env_file).read()
    assert "SECRETVALUE" in open(env_file).read()
