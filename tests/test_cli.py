
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
    assert 'initing' in run(['init'])
