from __future__ import annotations  # WARNING: remove this when debugging

import sys
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import cast

from dynaconf.base import LazySettings
from dynaconf.base import Settings as BaseDynaconfSettings
from dynaconf.utils.functional import Empty

from .utils import extract_defaults_and_validators_from_typing
from .utils import raise_for_invalid_class_variable

if sys.version_info < (3, 10):
    dclass_args: dict[str, Any] = {}
else:
    dclass_args = {"kw_only": True}


@dataclass(**dclass_args)
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
    root_path: str | Path | type = Empty
    settings_files: list[str] | type = Empty
    settings_file: str | type = Empty

    _trigger_validation: bool = True

    def as_dict(self):
        options_dict = asdict(self)
        options_dict = {
            k: v
            for k, v in options_dict.items()
            if (not k.startswith("_")) and v is not Empty
        }
        return options_dict


class Dynaconf(BaseDynaconfSettings):
    """Implementation of Dynaconf that is aware of type annotations."""

    dynaconf_options: Options

    def __new__(cls, *args, **kwargs):
        raise_for_invalid_class_variable(cls)
        options = getattr(cls, "dynaconf_options", Options())
        if not isinstance(options, Options):
            raise TypeError(
                "dynaconf_options must be an instance of `Options`"
            )
        defaults, validators = extract_defaults_and_validators_from_typing(cls)
        passed_in_validators = kwargs.pop("validators", [])
        validators += passed_in_validators

        # Set init options for Dynaconf coming first from Options on Schema
        init_options = options.as_dict()
        # Add defaults defined on class as it was passed to Dynaconf(k=v)
        # It will take first the default from cls, then from DictValue type.
        init_options.update(defaults)
        # Override from kwargs as if matching key was passed to Settings(k=v)
        init_options.update(kwargs)

        # Instantiate the new Dynaconf instance
        new_cls = LazySettings(*args, **init_options)
        new_cls.__annotations__ = cls.__annotations__

        if validators:
            new_cls.validators.register(*validators)

        # Trigger validation if not explicitly disabled
        if options._trigger_validation:
            new_cls.validators.validate_all()

        return cast(cls, new_cls)
