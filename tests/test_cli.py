import os
import pytest
from pathlib import Path
from click.testing import CliRunner
from dynaconf.cli import main, EXTS
from dotenv import cli as dotenv_cli


runner = CliRunner()


def run(cmd):
    result = runner.invoke(main, cmd)
    assert result.exit_code == 0
    return result.output


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
            '-v name=bruno',
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
        assert 'secret for' in open(secs).read()
        os.remove(secs)

    # gign = Path('.gitignore')
    # assert gign.exists() is True
    # assert ".secrets.*" in open(gign).read()


@pytest.mark.parametrize("fileformat", EXTS)
def test_init_with_path(fileformat):
    # run twice to force load of existing files
    if fileformat == 'env':
        path = '/tmp/.env'
        secs_path = None
    else:
        path = '/tmp/settings.{}'.format(fileformat)
        secs_path = '/tmp/.secrets.{}'.format(fileformat)

    for _ in (1, 2):
        run(
            [
                'init', '--no-wg',
                '--format={}'.format(fileformat),
                '--path={}'.format(path),
                '-y'
            ]
        )

    sets = Path(path)
    assert sets.exists() is True
    assert 'value for default' in open(sets).read()
    os.remove(sets)

    if secs_path:
        secs = Path('/tmp/.secrets.{}'.format(fileformat))
        assert secs.exists() is True
        assert 'secret for' in open(secs).read()
        os.remove(secs)

    # gign = Path('.gitignore')
    # assert gign.exists() is True
    # assert ".secrets.*" in open(gign).read()
