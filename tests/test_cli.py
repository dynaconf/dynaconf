import os
from pathlib import Path
from click.testing import CliRunner
from dynaconf.cli import main


runner = CliRunner()


def run(cmd):
    result = runner.invoke(main, cmd)
    assert result.exit_code == 0
    return result.output


def test_help():
    assert 'Dynaconf - Command Line Interface' in run(['--help'])


def test_banner():
    assert 'Learn more at:' in run(['banner'])


def test_init():
    run(['init', '-no-wg'])

    sets = Path('settings.toml')
    secs = Path('.secrets.toml')
    # gign = Path('.gitignore')

    assert sets.exists() is True
    assert secs.exists() is True
    # assert gign.exists() is True

    assert '[default]' in open(sets).read()
    assert 'secret for' in open(secs).read()
    # assert ".secrets.*" in open(gign).read()

    os.remove(sets)
    os.remove(secs)
