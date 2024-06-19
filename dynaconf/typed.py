"""Implements wrappers, types and helpers for Schema based settings."""

from __future__ import annotations  # WARNING: remove this when debugging

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from dynaconf.base import LazySettings as OriginalDynaconf
from dynaconf.base import Settings as BaseDynaconfSettings
from dynaconf.validator import ValidationError  # noqa
from dynaconf.validator import Validator


class Empty: ...


empty = Empty()


@dataclass  # wanted to pass (kw_only=True) but that works only for 3.10+
class Options:
    """Options to configure the initialization of Dynaconf Object.

    NOTE: This must be used only with typed implementation of Dynaconf.

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


class Nested: ...


class Dynaconf(BaseDynaconfSettings, Nested):
    """Implementation of Dynaconf that is aware of type annotations."""

    def __new__(cls, *args, **kwargs):
        options = getattr(cls, "dynaconf_options", Options())
        validators = kwargs.pop("validators", [])
        defaults = {}

        def handle_schema_class(schema_cls, path: tuple):
            # Extract Validators and default value from type Annotations:
            # name: _annotation = default_value or Empty
            for name, _annotation in schema_cls.__annotations__.items():
                default_value = getattr(schema_cls, name, empty)
                full_name = path + (name,)  # E.g, path.to.name
                if default_value is not empty:
                    defaults[".".join(full_name)] = default_value

                if isinstance(_annotation, type) and issubclass(
                    _annotation, Nested
                ):
                    handle_schema_class(_annotation, full_name)
                elif _validators := getattr(_annotation, "__metadata__", None):
                    # take the metadata from Annotated[type, *metadata]
                    for _validator in _validators:
                        _validator.names = [".".join(full_name)]
                        # take the type from Annotated[type, *metadata]
                        _validator.is_type_of = _annotation.__origin__
                        if default_value is empty:
                            _validator.must_exist = True  # required
                        validators.append(_validator)
                else:
                    _validator = Validator(name, is_type_of=_annotation)
                    if default_value is empty:
                        _validator.must_exist = True  # required
                    validators.append(_validator)

        handle_schema_class(cls, tuple())

        # Set init options for Dynaconf coming first from Options on Schema
        init_options = options.as_dict()
        # Add defaults defined on class as it was passed to Dynaconf(k=v)
        init_options.update(defaults)
        # Override from kwargs as if matching key was passed to Settings(k=v)
        init_options.update(kwargs)

        # Instantiate the new Dynaconf instance
        new_cls = OriginalDynaconf(*args, **init_options)
        new_cls.__annotations__ = cls.__annotations__

        # Alternative for setting defaults:
        # WARNING: This triggers the settings initialization
        # so it is not Lazy anymore, should we consider accumulating
        # default values somewhere and retrieving on `settings.get` ?
        # or add default_value to Validator above?
        #
        # for name, value in defaults.items():
        #     if new_cls.get(name, empty) is empty:
        #         new_cls.set(name, value, loader_identifier="type_annotations")

        if validators:
            new_cls.validators.register(*validators)

        # Trigger validation if not explicitly disabled
        if options._trigger_validation:
            new_cls.validators.validate()

        return cast(cls, new_cls)
