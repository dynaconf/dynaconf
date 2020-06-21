import importlib
import io
import os
import pprint
import sys
import warnings
import webbrowser
from contextlib import suppress
from pathlib import Path

import click
import toml
from dotenv import cli as dotenv_cli

from dynaconf import constants
from dynaconf import default_settings
from dynaconf import LazySettings
from dynaconf import loaders
from dynaconf import settings as legacy_settings
from dynaconf.loaders.py_loader import get_module
from dynaconf.utils import upperfy
from dynaconf.utils.files import read_file
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.validator import ValidationError
from dynaconf.validator import Validator


CWD = Path.cwd()
EXTS = ["ini", "toml", "yaml", "json", "py", "env"]
WRITERS = ["ini", "toml", "yaml", "json", "py", "redis", "vault", "env"]

ENC = default_settings.ENCODING_FOR_DYNACONF


def set_settings(ctx, instance=None):
    """Pick correct settings instance and set it to a global variable."""

    global settings

    settings = None

    if instance is not None:
        settings = import_settings(instance)
    elif "FLASK_APP" in os.environ:  # pragma: no cover
        with suppress(ImportError, click.UsageError):
            from flask.cli import ScriptInfo

            flask_app = ScriptInfo().load_app()
            settings = flask_app.config
            click.echo(
                click.style(
                    "Flask app detected", fg="white", bg="bright_black"
                )
            )
    elif "DJANGO_SETTINGS_MODULE" in os.environ:  # pragma: no cover
        sys.path.insert(0, os.path.abspath(os.getcwd()))
        try:
            # Django extension v2
            from django.conf import settings

            settings.DYNACONF.configure()
        except (ImportError, AttributeError):
            # Backwards compatible with old django extension (pre 2.0.0)
            import dynaconf.contrib.django_dynaconf  # noqa
            from django.conf import settings as django_settings

            django_settings.configure()
            settings = django_settings

        if settings is not None:
            click.echo(
                click.style(
                    "Django app detected", fg="white", bg="bright_black"
                )
            )

    if settings is None:

        if instance is None and "--help" not in click.get_os_args():
            if ctx.invoked_subcommand and ctx.invoked_subcommand not in [
                "init",
            ]:
                warnings.warn(
                    "Starting on 3.x the param --instance/-i is now required. "
                    "try passing it `dynaconf -i path.to.settings <cmd>`"
                )
                settings = legacy_settings
            else:
                settings = LazySettings(create_new_settings=True)
        else:
            settings = LazySettings()


def import_settings(dotted_path):
    """Import settings instance from python dotted path.

    Last item in dotted path must be settings instace.

    Example: import_settings('path.to.settings')
    """
    if "." in dotted_path:
        module, name = dotted_path.rsplit(".", 1)
    else:
        raise click.UsageError(
            f"invalid path to settings instance: {dotted_path}"
        )
    try:
        module = importlib.import_module(module)
    except ImportError as e:
        raise click.UsageError(e)
    try:
        return getattr(module, name)
    except AttributeError as e:
        raise click.UsageError(e)


def split_vars(_vars):
    """Splits values like foo=bar=zaz in {'foo': 'bar=zaz'}"""
    return (
        {
            upperfy(k.strip()): parse_conf_data(v.strip(), tomlfy=True)
            for k, _, v in [item.partition("=") for item in _vars]
        }
        if _vars
        else {}
    )


def read_file_in_root_directory(*names, **kwargs):
    """Read a file on root dir."""
    return read_file(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf-8"),
    )


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(read_file_in_root_directory("VERSION"))
    ctx.exit()


def open_docs(ctx, param, value):  # pragma: no cover
    if not value or ctx.resilient_parsing:
        return
    url = "http://dynaconf.readthedocs.io/"
    webbrowser.open(url, new=2)
    click.echo(f"{url} opened in browser")
    ctx.exit()


def show_banner(ctx, param, value):
    """Shows dynaconf awesome banner"""
    if not value or ctx.resilient_parsing:
        return
    set_settings(ctx)
    click.echo(settings.dynaconf_banner)
    click.echo("Learn more at: http://github.com/rochacbruno/dynaconf")
    ctx.exit()


@click.group()
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show dynaconf version",
)
@click.option(
    "--docs",
    is_flag=True,
    callback=open_docs,
    expose_value=False,
    is_eager=True,
    help="Open documentation in browser",
)
@click.option(
    "--banner",
    is_flag=True,
    callback=show_banner,
    expose_value=False,
    is_eager=True,
    help="Show awesome banner",
)
@click.option(
    "--instance",
    "-i",
    default=None,
    envvar="INSTANCE_FOR_DYNACONF",
    help="Custom instance of LazySettings",
)
@click.pass_context
def main(ctx, instance):
    """Dynaconf - Command Line Interface\n
    Documentation: http://dynaconf.readthedocs.io/
    """
    set_settings(ctx, instance)


@main.command()
@click.option(
    "--format", "fileformat", "-f", default="toml", type=click.Choice(EXTS)
)
@click.option(
    "--path", "-p", default=CWD, help="defaults to current directory"
)
@click.option(
    "--env", "-e", default=None, help="Sets the working env in `.env` file"
)
@click.option(
    "--vars",
    "_vars",
    "-v",
    multiple=True,
    default=None,
    help=(
        "extra values to write to settings file "
        "file e.g: `dynaconf init -v NAME=foo -v X=2"
    ),
)
@click.option(
    "--secrets",
    "_secrets",
    "-s",
    multiple=True,
    default=None,
    help=(
        "secret key values to be written in .secrets "
        "e.g: `dynaconf init -s TOKEN=kdslmflds"
    ),
)
@click.option("--wg/--no-wg", default=True)
@click.option("-y", default=False, is_flag=True)
@click.option("--django", default=os.environ.get("DJANGO_SETTINGS_MODULE"))
@click.pass_context
def init(ctx, fileformat, path, env, _vars, _secrets, wg, y, django):
    """Inits a dynaconf project
    By default it creates a settings.toml and a .secrets.toml
    for [default|development|staging|testing|production|global] envs.

    The format of the files can be changed passing
    --format=yaml|json|ini|py.

    This command must run on the project's root folder or you must pass
    --path=/myproject/root/folder.

    The --env/-e is deprecated (kept for compatibility but unused)
    """
    click.echo("Configuring your Dynaconf environment")
    path = Path(path)

    if settings.get("create_new_settings") is True:
        filename = Path("config.py")
        if not filename.exists():
            with open(filename, "w") as new_settings:
                new_settings.write(constants.INSTANCE_TEMPLATE)
        sys.path.append(str(path))
        set_settings(ctx, "config.settings")

    env = settings.current_env.lower()

    loader = importlib.import_module(f"dynaconf.loaders.{fileformat}_loader")
    # Turn foo=bar=zaz in {'foo': 'bar=zaz'}
    env_data = split_vars(_vars)
    _secrets = split_vars(_secrets)

    # create placeholder data for every env
    settings_data = {}
    secrets_data = {}
    if env_data:
        settings_data[env] = env_data
        settings_data["default"] = {k: "default" for k in env_data}
    if _secrets:
        secrets_data[env] = _secrets
        secrets_data["default"] = {k: "default" for k in _secrets}

    if str(path).endswith(
        constants.ALL_EXTENSIONS + ("py",)
    ):  # pragma: no cover  # noqa
        settings_path = path
        secrets_path = path.parent / f".secrets.{fileformat}"
        gitignore_path = path.parent / ".gitignore"
    else:
        if fileformat == "env":
            if str(path) in (".env", "./.env"):  # pragma: no cover
                settings_path = path
            elif str(path).endswith("/.env"):  # pragma: no cover
                settings_path = path
            elif str(path).endswith(".env"):  # pragma: no cover
                settings_path = path.parent / ".env"
            else:
                settings_path = path / ".env"
            Path.touch(settings_path)
            secrets_path = None
        else:
            settings_path = path / f"settings.{fileformat}"
            secrets_path = path / f".secrets.{fileformat}"
        gitignore_path = path / ".gitignore"

    if fileformat in ["py", "env"]:
        # for Python and .env files writes a single env
        settings_data = settings_data[env]
        secrets_data = secrets_data[env]

    if not y and settings_path and settings_path.exists():  # pragma: no cover
        click.confirm(
            f"{settings_path} exists do you want to overwrite it?", abort=True
        )

    if not y and secrets_path and secrets_path.exists():  # pragma: no cover
        click.confirm(
            f"{secrets_path} exists do you want to overwrite it?", abort=True
        )

    if settings_path and settings_data:
        loader.write(settings_path, settings_data, merge=True)
    if secrets_path and secrets_data:
        loader.write(secrets_path, secrets_data, merge=True)

    if wg:
        # write .gitignore
        ignore_line = ".secrets.*"
        comment = "\n# Ignore dynaconf secret files\n"
        if not gitignore_path.exists():
            with io.open(str(gitignore_path), "w", encoding=ENC) as f:
                f.writelines([comment, ignore_line, "\n"])
        else:
            existing = (
                ignore_line
                in io.open(str(gitignore_path), encoding=ENC).read()
            )
            if not existing:  # pragma: no cover
                with io.open(str(gitignore_path), "a+", encoding=ENC) as f:
                    f.writelines([comment, ignore_line, "\n"])

    if django:  # pragma: no cover
        dj_module, loaded_from = get_module({}, django)
        dj_filename = dj_module.__file__
        if Path(dj_filename).exists():
            click.confirm(
                f"{dj_filename} is found do you want to add dynaconf?",
                abort=True,
            )
            with open(dj_filename, "a") as dj_file:
                dj_file.write(constants.DJANGO_PATCH)
        else:
            click.echo("Django settings file not written.")


@main.command(name="list")
@click.option(
    "--env", "-e", default=None, help="Filters the env to get the values"
)
@click.option("--key", "-k", default=None, help="Filters a single key")
@click.option(
    "--more",
    "-m",
    default=None,
    help="Pagination more|less style",
    is_flag=True,
)
@click.option(
    "--loader",
    "-l",
    default=None,
    help="a loader identifier to filter e.g: toml|yaml",
)
@click.option(
    "--all",
    "_all",
    "-a",
    default=False,
    is_flag=True,
    help="show dynaconf internal settings?",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True, dir_okay=False),
    default=None,
    help="Filepath to write the listed values as json",
)
@click.option(
    "--output-flat",
    "flat",
    is_flag=True,
    default=False,
    help="Output file is flat (do not include [env] name)",
)
def _list(env, key, more, loader, _all=False, output=None, flat=False):
    """Lists all user defined config values
    and if `--all` is passed it also shows dynaconf internal variables.
    """
    if env:
        env = env.strip()
    if key:
        key = key.strip()
    if loader:
        loader = loader.strip()

    if env:
        settings.setenv(env)

    cur_env = settings.current_env.lower()

    if cur_env == "main":
        flat = True

    click.echo(
        click.style(
            f"Working in {cur_env} environment ",
            bold=True,
            bg="bright_blue",
            fg="bright_white",
        )
    )

    if not loader:
        data = settings.as_dict(env=env, internal=_all)
    else:
        identifier = f"{loader}_{cur_env}"
        data = settings._loaded_by_loaders.get(identifier, {})
        data = data or settings._loaded_by_loaders.get(loader, {})

    # remove to avoid displaying twice
    data.pop("SETTINGS_MODULE", None)

    def color(_k):
        if _k in dir(default_settings):
            return "blue"
        return "green"

    def format_setting(_k, _v):
        key = click.style(_k, bg=color(_k), fg="white")
        data_type = click.style(
            f"<{type(_v).__name__}>", bg="bright_black", fg="white"
        )
        value = pprint.pformat(_v)
        return f"{key}{data_type} {value}"

    if not key:
        datalines = "\n".join(
            format_setting(k, v)
            for k, v in data.items()
            if k not in data.get("RENAMED_VARS", [])
        )
        (click.echo_via_pager if more else click.echo)(datalines)
        if output:
            loaders.write(output, data, env=not flat and cur_env)
    else:
        key = upperfy(key)
        value = data.get(key)
        if not value:
            click.echo(click.style("Key not found", bg="red", fg="white"))
            return
        click.echo(format_setting(key, value))
        if output:
            loaders.write(output, {key: value}, env=not flat and cur_env)

    if env:
        settings.setenv()


@main.command()
@click.argument("to", required=True, type=click.Choice(WRITERS))
@click.option(
    "--vars",
    "_vars",
    "-v",
    multiple=True,
    default=None,
    help=(
        "key values to be written "
        "e.g: `dynaconf write toml -e NAME=foo -e X=2"
    ),
)
@click.option(
    "--secrets",
    "_secrets",
    "-s",
    multiple=True,
    default=None,
    help=(
        "secret key values to be written in .secrets "
        "e.g: `dynaconf write toml -s TOKEN=kdslmflds -s X=2"
    ),
)
@click.option(
    "--path",
    "-p",
    default=CWD,
    help="defaults to current directory/settings.{ext}",
)
@click.option(
    "--env",
    "-e",
    default="default",
    help=(
        "env to write to defaults to DEVELOPMENT for files "
        "for external sources like Redis and Vault "
        "it will be DYNACONF or the value set in "
        "$ENVVAR_PREFIX_FOR_DYNACONF"
    ),
)
@click.option("-y", default=False, is_flag=True)
def write(to, _vars, _secrets, path, env, y):
    """Writes data to specific source"""
    _vars = split_vars(_vars)
    _secrets = split_vars(_secrets)
    loader = importlib.import_module(f"dynaconf.loaders.{to}_loader")

    if to in EXTS:

        # Lets write to a file
        path = Path(path)

        if str(path).endswith(constants.ALL_EXTENSIONS + ("py",)):
            settings_path = path
            secrets_path = path.parent / f".secrets.{to}"
        else:
            if to == "env":
                if str(path) in (".env", "./.env"):  # pragma: no cover
                    settings_path = path
                elif str(path).endswith("/.env"):
                    settings_path = path
                elif str(path).endswith(".env"):
                    settings_path = path.parent / ".env"
                else:
                    settings_path = path / ".env"
                Path.touch(settings_path)
                secrets_path = None
                _vars.update(_secrets)
            else:
                settings_path = path / f"settings.{to}"
                secrets_path = path / f".secrets.{to}"

        if (
            _vars and not y and settings_path and settings_path.exists()
        ):  # pragma: no cover  # noqa
            click.confirm(
                f"{settings_path} exists do you want to overwrite it?",
                abort=True,
            )

        if (
            _secrets and not y and secrets_path and secrets_path.exists()
        ):  # pragma: no cover  # noqa
            click.confirm(
                f"{secrets_path} exists do you want to overwrite it?",
                abort=True,
            )

        if to not in ["py", "env"]:
            if _vars:
                _vars = {env: _vars}
            if _secrets:
                _secrets = {env: _secrets}

        if _vars and settings_path:
            loader.write(settings_path, _vars, merge=True)
            click.echo(f"Data successful written to {settings_path}")

        if _secrets and secrets_path:
            loader.write(secrets_path, _secrets, merge=True)
            click.echo(f"Data successful written to {secrets_path}")

    else:  # pragma: no cover
        # lets write to external source
        with settings.using_env(env):
            # make sure we're in the correct environment
            loader.write(settings, _vars, **_secrets)
        click.echo(f"Data successful written to {to}")


@main.command()
@click.option(
    "--path", "-p", default=CWD, help="defaults to current directory"
)
def validate(path):  # pragma: no cover
    """Validates Dynaconf settings based on rules defined in
    dynaconf_validators.toml"""
    # reads the 'dynaconf_validators.toml' from path
    # for each section register the validator for specific env
    # call validate

    path = Path(path)

    if not str(path).endswith(".toml"):
        path = path / "dynaconf_validators.toml"

    if not path.exists():  # pragma: no cover  # noqa
        click.echo(click.style(f"{path} not found", fg="white", bg="red"))
        sys.exit(1)

    validation_data = toml.load(open(str(path)))

    success = True
    for env, name_data in validation_data.items():
        for name, data in name_data.items():
            if not isinstance(data, dict):  # pragma: no cover
                click.echo(
                    click.style(
                        f"Invalid rule for parameter '{name}'",
                        fg="white",
                        bg="yellow",
                    )
                )
            else:
                data.setdefault("env", env)
                click.echo(
                    click.style(
                        f"Validating '{name}' with '{data}'",
                        fg="white",
                        bg="blue",
                    )
                )
                try:
                    Validator(name, **data).validate(settings)
                except ValidationError as e:
                    click.echo(
                        click.style(f"Error: {e}", fg="white", bg="red")
                    )
                    success = False

    if success:
        click.echo(click.style("Validation success!", fg="white", bg="green"))
    else:
        click.echo(click.style("Validation error!", fg="white", bg="red"))
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
