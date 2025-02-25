from __future__ import annotations

# WARNING: remove the import above when debugging on Python 3.12
# otherwise type annotations will be stringified.
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from dynaconf.base import LazySettings
from dynaconf.base import Settings as BaseDynaconfSettings
from dynaconf.typed import guards as gu
from dynaconf.typed import utils as ut
from dynaconf.utils.functional import Empty

from .parser import parse_schema


@dataclass
class Options:
    """Options to configure the initialization of typed.Dynaconf Object.

    All options are just bypassed to the Dynaconf `__init__` method,
    except those starting with `_`.

    Options starting with `_` are only used on `__new__` when building the
    new Dynaconf object, those values assumes opinionated defaults and rarely
    needs to be changed.
    """

    # NOTE: On a dataclass the sentinel must be a Type not an instance

    env: str | type = Empty
    environments: bool | type = Empty
    envvar_prefix: str | type = Empty
    env_switcher: str | type = Empty
    root_path: str | Path | type = Empty
    settings_files: list[str] | type = Empty
    settings_file: str | type = Empty
    load_dotenv: bool | type = Empty

    trigger_validation: bool = True

    def as_dict(self):
        return {
            k: v
            for k, v in asdict(self).items()
            if (not k.startswith("_")) and v is not Empty
        }


class Dynaconf(BaseDynaconfSettings):
    """Interface to create an instance of Dynaconf based on typing.

    This class is a builder for a new instance of Dynaconf with validators
    and default values extracted from subclass type annotations and attributes.
    """

    __reserved__: dict = {}
    dynaconf_options: Options

    def __new__(cls, *args, **kwargs):
        gu.raise_for_invalid_class_variable(cls)
        options = getattr(cls, "dynaconf_options", Options())
        if not isinstance(options, Options):
            raise TypeError(
                "dynaconf_options must be an instance of `Options`"
            )
        schema = parse_schema(cls)
        defaults = schema.defaults
        validators = schema.validators

        passed_in_validators = kwargs.pop("validators", [])
        validators += passed_in_validators

        init_options = ut.multi_dict_merge(
            options.as_dict(), defaults, kwargs, {"DYNABOXIFY": False}
        )

        # Useful while writing tests
        if kwargs.pop("_debug_mode", None):
            ut.dump_debug_info(init_options, validators, schema)

        new_cls = LazySettings(*args, **init_options)
        # new_cls.__annotations__ = cls.__annotations__

        if validators:
            new_cls.validators.register(*validators)

        # Trigger validation if not explicitly disabled
        if options.trigger_validation:
            new_cls.validators.validate_all()

        return cast(cls, new_cls)
