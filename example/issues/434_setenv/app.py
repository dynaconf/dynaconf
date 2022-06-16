from __future__ import annotations

import click

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
)


@click.group()
@click.option("--config", default="default")
def main(config):
    click.echo(f"Environment: {config}")
    settings.setenv(config)
    return


@main.command()
def dynaconf():
    click.echo(f"Database Path: {settings.DB_PATH}")
    assert "/mydb.db" in settings.DB_PATH
    return


if __name__ == "__main__":
    main()
