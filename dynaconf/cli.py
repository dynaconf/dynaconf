import click
from pathlib import Path
from dynaconf import settings
from dynaconf import loaders
from dynaconf import constants
from dotenv import cli as dotenv_cli


CWD = Path.cwd()
ENVS = ['default', 'development', 'staging', 'testing', 'production', 'global']
EXTS = ['ini', 'toml', 'yaml', 'json', 'py']


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
@click.option('--env', default='default', type=click.Choice(ENVS),
              help='Sets the working env in `.env` file')
@click.option('--envvars', '-e', multiple=True, default=None,
              help=(
                  'extra global envvars to include in `.env` '
                  'file e.g: `dynaconf init -e NAME=foo -e X=2'
              ))
@click.option('-wg/-no-wg', default=True)
@click.option('-y', default=False, is_flag=True)
def init(fileformat, path, env, envvars, wg, y):
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
    env_data = {k.upper(): v
                for k, _, v
                in [item.partition('=') for item in envvars]}

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
