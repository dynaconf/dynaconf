import os
import pytest
from pathlib import Path
from click.testing import CliRunner
from dynaconf.cli import main, EXTS


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
    run(
        [
            'init',
            '-no-wg',
            '--format={}'.format(fileformat),
            '-v name=bruno',
            '-y'
        ]
    )

    sets = Path('settings.{}'.format(fileformat))
    secs = Path('.secrets.{}'.format(fileformat))
    # gign = Path('.gitignore')

    assert sets.exists() is True
    assert secs.exists() is True
    # assert gign.exists() is True

    assert 'bruno' in open(sets).read()
    assert 'secret for' in open(secs).read()
    # assert ".secrets.*" in open(gign).read()

    os.remove(sets)
    os.remove(secs)


@pytest.mark.parametrize("fileformat", EXTS)
def test_init_with_path(fileformat):
    # run twice to force load of existing files
    for _ in (1, 2):
        run(
            [
                'init', '-no-wg',
                '--format={}'.format(fileformat),
                '--path=/tmp/settings.{}'.format(fileformat),
                '-y'
            ]
        )

    sets = Path('/tmp/settings.{}'.format(fileformat))
    secs = Path('/tmp/.secrets.{}'.format(fileformat))
    # gign = Path('.gitignore')

    assert sets.exists() is True
    assert secs.exists() is True
    # assert gign.exists() is True

    assert 'value for default' in open(sets).read()
    assert 'secret for' in open(secs).read()
    # assert ".secrets.*" in open(gign).read()

    os.remove(sets)
    os.remove(secs)
