import click
import pprint
from pathlib import Path
from dynaconf import settings
from dynaconf import loaders
from dynaconf import constants
from dynaconf.utils.parse_conf import parse_conf_data
from dotenv import cli as dotenv_cli


CWD = Path.cwd()
ENVS = ['default', 'development', 'staging', 'testing', 'production', 'global']
EXTS = ['ini', 'toml', 'yaml', 'json', 'py']
WRITERS = ['ini', 'toml', 'yaml', 'json', 'py', 'redis', 'vault']


def split_vars(vars):
    """Splits values like foo=bar=zaz in {'foo': 'bar=zaz'}"""
    return {
        k.upper(): parse_conf_data(v)
        for k, _, v
        in [item.partition('=') for item in vars]
    }


@click.group()
def main():
    """Dynaconf - Command Line Interface"""


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
@click.option('--env', '-e', default='default', type=click.Choice(ENVS),
              help='Sets the working env in `.env` file')
@click.option('--vars', '_vars', '-v', multiple=True, default=None,
              help=(
                  'extra global envvars to include in `.env` '
                  'file e.g: `dynaconf init -v NAME=foo -v X=2'
              ))
@click.option('-wg/-no-wg', default=True)
@click.option('-y', default=False, is_flag=True)
def init(fileformat, path, env, _vars, wg, y):
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

    loader = getattr(loaders, "{}_loader".format(fileformat))
    # Turn foo=bar=zaz in {'foo': 'bar=zaz'}
    env_data = split_vars(_vars)

    # create placeholder data for every env
    settings_data = {k: {'value': 'value for {}'.format(k)} for k in ENVS}
    secrets_data = {k: {'secret': 'secret for {}'.format(k)} for k in ENVS}
    if env_data:
        settings_data[env] = env_data

    path = Path(path)

    if str(path).endswith(constants.ALL_EXTENSIONS + ('py',)):
        settings_path = path
        secrets_path = path.parent / '.secrets.{}'.format(fileformat)
        dotenv_path = path.parent / '.env'
        gitignore_path = path.parent / '.gitignore'
    else:
        settings_path = path / 'settings.{}'.format(fileformat)
        secrets_path = path / '.secrets.{}'.format(fileformat)
        dotenv_path = path / '.env'
        gitignore_path = path / '.gitignore'

    if fileformat == 'py':
        # for Python and .env files writes a single env
        settings_data = settings_data[env]
        secrets_data = secrets_data[env]

    if not y and settings_path.exists():  # pragma: no cover
        click.confirm(
            '{} exists do you want to overwrite it?'.format(settings_path),
            abort=True
        )

    if not y and secrets_path.exists():  # pragma: no cover
        click.confirm(
            '{} exists do you want to overwrite it?'.format(secrets_path),
            abort=True
        )

    loader.write(settings_path, settings_data, merge=True)
    loader.write(secrets_path, secrets_data, merge=True)

    # write .env file
    if env not in ['default', 'development']:  # pragma: no cover
        Path.touch(dotenv_path)
        dotenv_cli.set_key(str(dotenv_path), 'ENV_FOR_DYNACONF', env.upper())

    if wg:  # pragma: no cover
        # write .gitignore
        ignore_line = ".secrets.*"
        comment = "\n# Ignore dynaconf secret files\n"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.writelines([comment, ignore_line, '\n'])
        else:
            existing = ignore_line in open(gitignore_path).read()
            if not existing:
                with open(gitignore_path, 'a+') as f:
                    f.writelines(
                        [comment, ignore_line, '\n']
                    )


@main.command()
@click.option('--env', '-e', default=None,
              help='Filters the env to get the values')
@click.option('--key', '-k', default=None, help='Filters a single key')
@click.option('--more', '-m', default=None,
              help='Pagination more|less style', is_flag=True)
@click.option('--loader', '-l', default=None,
              help='a loader identifier to filter e.g: toml|yaml')
def list(env, key, more, loader):
    """Lists all defined config values"""
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

    if not key:
        datalines = '\n'.join(
            '%s: %s' % (click.style(k, bg='green', fg='white'),
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
                click.style(key.upper(), bg='green', fg='white'),
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
@click.option('--path', '-p', default=CWD,
              help='defaults to current directory/settings.{ext}')
@click.option(
    '--env', '-e', default='default', type=click.Choice(ENVS),
    help=(
        'env to write to defaults to DEVELOPMENT for files '
        'for external sources like Redis and Vault '
        'it will be DYNACONF or the value set in '
        '$GLOBAL_ENV_FOR_DYNACONF'
    )
)
@click.option('-y', default=False, is_flag=True)
def write(to, _vars, path, env, y):
    """Writes data to specific source"""
    _vars = split_vars(_vars)

    if to in EXTS:
        # Lets write to a file
        path = Path(path)
        if str(path).endswith(constants.ALL_EXTENSIONS + ('py',)):
            settings_path = path
            secrets_path = path.parent / '.secrets.{}'.format(to)
            # dotenv_path = path.parent / '.env'
        else:
            settings_path = path / 'settings.{}'.format(to)
            secrets_path = path / '.secrets.{}'.format(to)
            # dotenv_path = path / '.env'

        if not y and settings_path.exists():  # pragma: no cover
            click.confirm(
                '{} exists do you want to overwrite it?'.format(settings_path),
                abort=True
            )

        if not y and secrets_path.exists():  # pragma: no cover
            click.confirm(
                '{} exists do you want to overwrite it?'.format(secrets_path),
                abort=True
            )

        if to not in ['py', 'env']:
            _vars = {env: _vars}

        loader = getattr(loaders, "{}_loader".format(to))
        loader.write(settings_path, _vars, merge=True)
        loader.write(secrets_path, _vars, merge=True)

    else:
        # lets get external loader
        pass
