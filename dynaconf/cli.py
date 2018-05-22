import click
from pathlib import Path
from dynaconf import settings


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
@click.option('--format', '-f', default='toml', type=click.Choice(EXTS))
@click.option('--path', '-p', default=CWD,
              help='defaults to current directory')
@click.option('--env', default=None, type=click.Choice(ENVS),
              help='Sets the working env in `.env` file')
@click.option('--envvars', '-e', multiple=True, default=None,
              help=(
                  'extra global envvars to include in `.env` '
                  'file e.g: `dynaconf init -e NAME=foo -e X=2'
              ))
def init(format, path, env, envvars):
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
    click.echo('initing')
