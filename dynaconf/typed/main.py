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
from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from . import guards as gu
from . import types as ty
from . import utils as ut
from .compat import get_annotations

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
        gu.raise_for_invalid_class_variable(cls)
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


def extract_defaults_and_validators_from_typing(
    schema_cls,
    path: tuple | None = None,
    defaults: dict | None = None,
    validators: list | None = None,
) -> tuple[dict, list]:
    """From schema class extract defaults and validators from annotations.

    Recursively handle all `DictValue` subtypes.

    key: int -> Validator(key, is_type_of=int)
    key: int = 1 -> Validator(key, is_type_of=int) + defaults[key] = 1
    key: Annotated[int, Validator()] -> Validator(key, is_type_of=int)
    """
    # These names passes down recursively
    path = path or tuple()
    defaults = defaults or {}
    validators = validators or []

    for name, annotation in get_annotations(schema_cls).items():
        if name == "dynaconf_options":
            # In case someone does dyanconf_options: Options = Options(...)
            # That value is kept out of the schema validation
            continue

        default_value = getattr(schema_cls, name, empty)
        full_path = path + (name,)  # E.g, ("path", "to", "name")
        full_name = ".".join(full_path)  # E.g, path.to.name
        _type, _type_args, _args_validators = ut.get_type_and_args(annotation)
        gu.raise_for_unsupported_type(full_name, _type, _type_args, annotation)
        is_notrequired = False

        if _args_validators and isinstance(
            _args_validators[0], ty._NotRequiredMarker
        ):
            # Annotated[NotRequired[T], ...]
            _, *_args_validators = _args_validators
            is_notrequired = True
        if _args_validators and isinstance(
            _args_validators[-1], ty._NotRequiredMarker
        ):
            # NotRequired[Annotated[T, ...]]
            *_args_validators, _ = _args_validators
            is_notrequired = True

        if default_value is not empty:
            previous_default = defaults.get(".".join(path))
            already_defined = (
                isinstance(previous_default, dict) and name in previous_default
            )
            if not already_defined:
                defaults[full_name] = default_value

        gu.raise_for_optional_without_none(
            full_name, _type, _type_args, default_value, annotation
        )

        # field: DictValue
        if ut.is_dict_value(annotation):
            _validator = BaseValidator(full_name, is_type_of=annotation)
            if default_value is empty and not is_notrequired:
                _validator.must_exist = True
            validators.append(_validator)
            # Recursively call this same function until all nested exhausts.
            defaults, validators = extract_defaults_and_validators_from_typing(
                annotation, full_path, defaults, validators
            )
        # field: Annotated[T, Validator(...)]
        elif _args_validators:
            gu.raise_for_invalid_annotated(full_name, _type, _args_validators)
            # add one base validator for type checking
            _validator = BaseValidator(full_name, is_type_of=_type)
            if default_value is empty and not is_notrequired:
                _validator.must_exist = True
            validators.append(_validator)
            # Add all the extra validators added via Annotated args
            for _validator in _args_validators:
                _validator.names = (full_name,)
                validators.append(_validator)
            if ut.is_dict_value(_type):
                # Recursively call this same function until all nested exhausts.
                defaults, validators = (
                    extract_defaults_and_validators_from_typing(
                        _type, full_path, defaults, validators
                    )
                )
        # field: list[T]
        elif ut.is_enclosed_list(_type, _type_args):
            _validator = BaseValidator(full_name, is_type_of=_type)
            inner_type, *more_types = _type_args

            # NOT SURE ABOUT THIS
            gu.raise_for_invalid_amount_of_enclosed_types(
                full_name, _type, inner_type, more_types
            )

            # In case of list[DictValue]
            enclosed_defaults, enclosed_validators = (
                extract_defaults_and_validators_from_typing(inner_type)
            )
            gu.raise_for_enclosed_with_defaults(
                full_name, _type, inner_type, enclosed_defaults, annotation
            )

            _validator.condition = ut.validator_condition_factory(
                enclosed_validators, full_name, inner_type
            )

            if default_value is empty and not is_notrequired:
                _validator.must_exist = True  # required

            validators.append(_validator)
        # field: T
        else:
            # print()
            # print("AAAAAAAA", full_name, _type, annotation)
            # hook creation of validators for Optional and Notrequired here

            _validator = BaseValidator(full_name)
            if default_value is empty and not is_notrequired:
                _validator.must_exist = True  # required

            if is_notrequired:
                # Extract the types from the Annotated
                if ut.is_dict_value(annotation):
                    _validator.is_type_of = annotation
                else:
                    _validator.is_type_of = _type
            else:
                _validator.is_type_of = annotation

            validators.append(_validator)

    return defaults, validators
