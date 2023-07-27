from __future__ import annotations

import argparse

from dynaconf import settings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Simple argparse example for overwrite dynaconf settings"
    )

    parser.add_argument("--env", default=settings.current_env)
    parser.add_argument("--host", default=settings.HOST)
    parser.add_argument("--port", default=settings.PORT)

    options, args = parser.parse_known_args(argv)

    # change the environment to update proper settings
    settings.setenv(options.env)

    # update the dynaconfig settings
    settings.update(vars(options))

    assert options.host == settings.HOST
    assert options.port == settings.PORT
    assert options.env == settings.current_env

    # ensure that other env didn't change
    with settings.using_env("staging"):
        assert options.host != settings.HOST
        assert options.env != settings.current_env


if __name__ == "__main__":
    main(argv=None)
