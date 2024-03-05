from __future__ import annotations

import click

from dynaconf import settings


@click.command()
@click.option("--host", default=settings.HOST, help="Host")
@click.option("--port", default=settings.PORT, help="Port")
@click.option("--env", default=settings.current_env, help="Env")
def app(**options):
    """Simple click example for overwrite dynaconf settings"""

    # change the environment to update proper settings
    settings.setenv(options["env"])

    # update the dynaconfig settings
    settings.update(options)

    assert options["host"] == settings.HOST
    assert options["port"] == settings.PORT
    assert options["env"] == settings.current_env

    # ensure that other env didn't change
    with settings.using_env("staging"):
        assert options["host"] != settings.HOST
        assert options["env"] != settings.current_env


if __name__ == "__main__":
    app()
