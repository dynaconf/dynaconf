from __future__ import annotations

import types
from dataclasses import asdict
from dataclasses import field
from typing import Callable

from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from . import exceptions as ex
from . import guards as gu
from . import types as ty
from . import utils as ut
from .compat import _dataclass
from .compat import get_annotations
from .compat import Self


@_dataclass
class Spec:
    type_class: type
    """The type for the value."""
    properties: dict[str, Self] = field(default_factory=dict)
    """Mapping for nested objects."""
    transformer: Callable | None = None
    """A callable to apply transformation upon loading."""
    items: Spec | None = None
    """Item spec for list objects."""
    doc: str = ""
    """Documentaion text"""

    def as_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@_dataclass
class ParsedSchema:
    defaults: dict
    validators: list[BaseValidator]
    schema: dict[str, Spec]

    def as_dict(self):
        return asdict(self)


def parse_schema(cls) -> ParsedSchema:
    """Extracts defaults and validators from a cls.

    This function is used on the main typed.Dynaconf and types.DataDict
    """
    defaults = {}
    validators = []
    schema = {}

    for name, annotation in get_annotations(cls).items():
        if name == "dynaconf_options":
            # In case someone does dynaconf_options: Options = Options(...)
            # That value is kept out of the schema validation
            continue

        # deal with attributes named against reserved methods e.g: copy
        value = cls.__reserved__.get(name, getattr(cls, name, empty))
        value_is_method = isinstance(value, types.MethodDescriptorType)

        if value is not empty and not value_is_method:
            # set default earlier, so if it is a Lazy str it resolves later
            defaults[name] = value

        # Annotation[T, args], list[T], NotRequired[T], dict[T,T]
        target_type, type_args = ut.get_type_and_args(annotation)
        gu.raise_for_unsupported_type(name, target_type, type_args, annotation)

        marked_not_required = False
        validator = BaseValidator(name, is_type_of=annotation)
        spec = schema[name] = Spec(type_class=annotation)

        annotated_validators: list[BaseValidator] = []
        extra_validators: list[BaseValidator] = []

        if ut.is_annotated(annotation):
            validator = BaseValidator(name, is_type_of=target_type)
            spec.type_class = target_type

            # here is where we extract markers and validator from Annotated
            for arg in type_args:
                if isinstance(arg, ty.NotRequiredMarker):
                    marked_not_required = True
                elif isinstance(arg, BaseValidator):
                    arg.names = (name,)
                    annotated_validators.append(arg)
                    # Would use combined validators? validator &= arg
                else:
                    _type = target_type
                    raise ex.DynaconfSchemaError(
                        f"Invalid Annotated Arg: {arg} "
                        f"this error is caused by "
                        f"`{name}: Annotated[{ut.get_type_name(_type)!r}"
                        f", {', '.join(str(i) for i in type_args)}]`"
                    )

        if value is empty and not marked_not_required:
            validator.must_exist = True

        if ut.is_dict_value(target_type):
            if isinstance(value, target_type):
                instance = defaults[name] = value
            elif isinstance(value, dict):
                instance = defaults[name] = target_type(value)
            else:
                instance = target_type()
                if instance and not marked_not_required:
                    defaults[name] = instance

            validator.items_validators = instance.__schema__.validators
            spec.properties = instance.__schema__.schema

            if instance:
                validator.must_exist = None  # can't be False

        elif (
            ut.is_enclosed_list(target_type, type_args)  # list[T]
            and ut.is_dict_value(type_args[0])  # list[DataDict]
        ):
            instance_class = type_args[0]
            instance = instance_class()
            validator.items_validators = instance.__schema__.validators
            spec.type_class = list
            spec.items = Spec(
                type_class=dict,
                transformer=instance_class,
            )
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        value[i] = instance_class(item)

        elif ut.maybe_dict_value(annotation):  # Optional[T], Union[T, T]
            instance_class = ut.get_class_from_type_args(type_args)
            instance = instance_class()

            if isinstance(value, dict):
                instance.update(value)
                defaults[name] = instance

            # NOTE: combine ORValidator here in case of
            # Union[DictValue, DictValue, ...]
            extra_validator = BaseValidator(
                name,
                items_validators=instance.__schema__.validators,
                when=BaseValidator(name, is_type_of=dict),
            )
            extra_validators.append(extra_validator)

        elif ut.is_dict_value_in_a_dict(annotation):  # dict[T, DataDict]
            instance_class = type_args[1]
            instance = instance_class()
            validator.items_validators = instance.__schema__.validators
            validator.items_lookup = lambda item: item.values()

            if isinstance(value, dict):
                for k, v in value.items():  # {T: {.}}
                    if isinstance(v, dict):
                        value[k] = instance_class(v)

        validators.append(validator)
        validators.extend(annotated_validators)
        validators.extend(extra_validators)

    # return defaults, validators
    return ParsedSchema(
        defaults=defaults,
        validators=validators,
        schema=schema,
    )
