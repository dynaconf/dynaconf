import io
import os
import click
import pprint
import importlib
import webbrowser
from pathlib import Path
from dynaconf import settings, default_settings
from dynaconf import constants
from dynaconf.utils.parse_conf import parse_conf_data
from dotenv import cli as dotenv_cli


CWD = Path.cwd()
ENVS = ['default', 'development', 'staging', 'testing', 'production', 'global']
EXTS = ['ini', 'toml', 'yaml', 'json', 'py', 'env']
WRITERS = ['ini', 'toml', 'yaml', 'json', 'py', 'redis', 'vault', 'env']


def split_vars(_vars):
    """Splits values like foo=bar=zaz in {'foo': 'bar=zaz'}"""
    return {
        k.upper().strip(): parse_conf_data(v.strip(), tomlfy=True)
        for k, _, v
        in [item.partition('=') for item in _vars]
    } if _vars else {}


def read(*names, **kwargs):
    """Read a file."""
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read().strip()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(read('VERSION'))
    ctx.exit()


def open_docs(ctx, param, value):  # pragma: no cover
    if not value or ctx.resilient_parsing:
        return
    url = 'http://dynaconf.readthedocs.io/'
    webbrowser.open(url, new=2)
    click.echo("{} opened in browser".format(url))
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show dynaconf version")
@click.option('--docs', is_flag=True, callback=open_docs, expose_value=False,
              is_eager=True, help="Open documentation in browser")
def main():
    """Dynaconf - Command Line Interface\n
    Documentation: http://dynaconf.readthedocs.io/
    """


@main.command()
def banner():
    """Shows dynaconf awesome banner"""
    click.echo(settings.dynaconf_banner)
    click.echo('Learn more at: http://github.com/rochacbruno/dynaconf')


@main.command()
@click.option('--format', 'fileformat', '-f', default='toml',
              type=click.Choice(EXTS))
@click.option('--path', '-p', default=CWD,
              help='defaults to current directory')
@click.option('--env', '-e', default=None,
              help='Sets the working env in `.env` file')
@click.option('--vars', '_vars', '-v', multiple=True, default=None,
              help=(
                  'extra values to write to settings file '
                  'file e.g: `dynaconf init -v NAME=foo -v X=2'
              ))
@click.option('--secrets', '_secrets', '-s', multiple=True, default=None,
              help=(
                  'secret key values to be written in .secrets '
                  'e.g: `dynaconf init -s TOKEN=kdslmflds'
              ))
@click.option('--wg/--no-wg', default=True)
@click.option('-y', default=False, is_flag=True)
def init(fileformat, path, env, _vars, _secrets, wg, y):
    """Inits a dynaconf project
    By default it creates a settings.toml and a .secrets.toml
    for [default|development|staging|testing|production|global] envs.

    The format of the files can be changed passing
    --format=yaml|json|ini|py.

    This command must run on the project's root folder or you must pass
    --path=/myproject/root/folder.

    If you want to have a .env created with the ENV defined there e.g:
    `ENV_FOR_DYNACONF=production` just pass --env=production and then .env
    will also be created and the env defined to production.
    """
    click.echo('Cofiguring your Dynaconf environment')

    env = env or settings.current_env.lower()

    loader = importlib.import_module(
        "dynaconf.loaders.{}_loader".format(fileformat)
    )
    # Turn foo=bar=zaz in {'foo': 'bar=zaz'}
    env_data = split_vars(_vars)
    _secrets = split_vars(_secrets)

    # create placeholder data for every env
    settings_data = {k: {'value': 'value for {}'.format(k)} for k in ENVS}
    secrets_data = {k: {'secret': 'secret for {}'.format(k)} for k in ENVS}
    if env_data:
        settings_data[env] = env_data
        settings_data['default'] = {k: 'default' for k in env_data}
    if _secrets:
        secrets_data[env] = _secrets
        secrets_data['default'] = {k: 'default' for k in _secrets}

    path = Path(path)

    if str(path).endswith(constants.ALL_EXTENSIONS + ('py',)):
        settings_path = path
        secrets_path = path.parent / '.secrets.{}'.format(fileformat)
        dotenv_path = path.parent / '.env'
        gitignore_path = path.parent / '.gitignore'
    else:
        if fileformat == 'env':
            if str(path) in ('.env', './.env'):  # pragma: no cover
                settings_path = path
            elif str(path).endswith('/.env'):
                settings_path = path
            elif str(path).endswith('.env'):  # pragma: no cover
                settings_path = path.parent / '.env'
            else:
                settings_path = path / '.env'
            Path.touch(settings_path)
            secrets_path = None
        else:
            settings_path = path / 'settings.{}'.format(fileformat)
            secrets_path = path / '.secrets.{}'.format(fileformat)
        dotenv_path = path / '.env'
        gitignore_path = path / '.gitignore'

    if fileformat in ['py', 'env']:
        # for Python and .env files writes a single env
        settings_data = settings_data[env]
        secrets_data = secrets_data[env]

    if not y and settings_path and settings_path.exists():  # pragma: no cover
        click.confirm(
            '{} exists do you want to overwrite it?'.format(settings_path),
            abort=True
        )

    if not y and secrets_path and secrets_path.exists():  # pragma: no cover
        click.confirm(
            '{} exists do you want to overwrite it?'.format(secrets_path),
            abort=True
        )

    if settings_path and settings_data:
        loader.write(settings_path, settings_data, merge=True)
    if secrets_path and secrets_data:
        loader.write(secrets_path, secrets_data, merge=True)

    # write .env file
    if env not in ['default', 'development']:  # pragma: no cover
        Path.touch(dotenv_path)
        dotenv_cli.set_key(str(dotenv_path), 'ENV_FOR_DYNACONF', env.upper())

    if wg:
        # write .gitignore
        ignore_line = ".secrets.*"
        comment = "\n# Ignore dynaconf secret files\n"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.writelines([comment, ignore_line, '\n'])
        else:
            existing = ignore_line in open(gitignore_path).read()
            if not existing:  # pragma: no cover
                with open(gitignore_path, 'a+') as f:
                    f.writelines(
                        [comment, ignore_line, '\n']
                    )


@main.command(name='list')
@click.option('--env', '-e', default=None,
              help='Filters the env to get the values')
@click.option('--key', '-k', default=None, help='Filters a single key')
@click.option('--more', '-m', default=None,
              help='Pagination more|less style', is_flag=True)
@click.option('--loader', '-l', default=None,
              help='a loader identifier to filter e.g: toml|yaml')
def _list(env, key, more, loader):
    """Lists all defined config values"""
    if env:
        env = env.strip()
    if key:
        key = key.strip()
    if loader:
        loader = loader.strip()

    if env:
        settings.setenv(env)

    cur_env = settings.current_env.lower()

    click.echo(
        click.style(
            'Working in %s environment ' % cur_env,
            bold=True, bg='blue', fg='white'
        )
    )

    if not loader:
        data = settings.store
    else:
        identifier = '{}_{}'.format(loader, cur_env)
        data = settings._loaded_by_loaders.get(identifier, {})
        data = data or settings._loaded_by_loaders.get(loader, {})

    def color(_k):
        if _k in dir(default_settings):
            return 'blue'
        return 'green'

    if not key:
        datalines = '\n'.join(
            '%s: %s' % (click.style(k, bg=color(k), fg='white'),
                        pprint.pformat(v))
            for k, v in data.items()
        )
        (click.echo_via_pager if more else click.echo)(datalines)
    else:
        key = key.upper()
        value = data.get(key)
        if not value:
            click.echo(click.style('Key not found', bg='red', fg='white'))
            return
        click.echo(
            '%s: %s' % (
                click.style(key.upper(), bg=color(key), fg='white'),
                pprint.pformat(value)
            )
        )

    if env:
        settings.setenv()


@main.command()
@click.argument('to', '--to', required=True, type=click.Choice(WRITERS))
@click.option('--vars', '_vars', '-v', multiple=True, default=None,
              help=(
                  'key values to be written '
                  'e.g: `dynaconf write --to toml -e NAME=foo -e X=2'
              ))
@click.option('--secrets', '_secrets', '-s', multiple=True, default=None,
              help=(
                  'secret key values to be written in .secrets '
                  'e.g: `dynaconf write --to toml -s TOKEN=kdslmflds -s X=2'
              ))
@click.option('--path', '-p', default=CWD,
              help='defaults to current directory/settings.{ext}')
@click.option(
    '--env', '-e', default='default',
    help=(
        'env to write to defaults to DEVELOPMENT for files '
        'for external sources like Redis and Vault '
        'it will be DYNACONF or the value set in '
        '$GLOBAL_ENV_FOR_DYNACONF'
    )
)
@click.option('-y', default=False, is_flag=True)
def write(to, _vars, _secrets, path, env, y):
    """Writes data to specific source"""
    _vars = split_vars(_vars)
    _secrets = split_vars(_secrets)
    loader = importlib.import_module("dynaconf.loaders.{}_loader".format(to))

    if to in EXTS:

        # Lets write to a file
        path = Path(path)

        if str(path).endswith(constants.ALL_EXTENSIONS + ('py',)):
            settings_path = path
            secrets_path = path.parent / '.secrets.{}'.format(to)
        else:
            if to == 'env':
                if str(path) in ('.env', './.env'):  # pragma: no cover
                    settings_path = path
                elif str(path).endswith('/.env'):
                    settings_path = path
                elif str(path).endswith('.env'):
                    settings_path = path.parent / '.env'
                else:
                    settings_path = path / '.env'
                Path.touch(settings_path)
                secrets_path = None
                _vars.update(_secrets)
            else:
                settings_path = path / 'settings.{}'.format(to)
                secrets_path = path / '.secrets.{}'.format(to)

        if _vars and not y and settings_path and settings_path.exists():  # pragma: no cover  # noqa
            click.confirm(
                '{} exists do you want to overwrite it?'.format(settings_path),
                abort=True
            )

        if _secrets and not y and secrets_path and secrets_path.exists():  # pragma: no cover  # noqa
            click.confirm(
                '{} exists do you want to overwrite it?'.format(secrets_path),
                abort=True
            )

        if to not in ['py', 'env']:
            if _vars:
                _vars = {env: _vars}
            if _secrets:
                _secrets = {env: _secrets}

        if _vars and settings_path:
            loader.write(settings_path, _vars, merge=True)
            click.echo('Data successful written to {}'.format(settings_path))

        if _secrets and secrets_path:
            loader.write(secrets_path, _secrets, merge=True)
            click.echo('Data successful written to {}'.format(secrets_path))

    else:  # pragma: no cover
        # lets write to external source
        loader.write(settings, _vars, **_secrets)
        click.echo('Data successful written to {}'.format(to))
