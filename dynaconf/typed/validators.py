from __future__ import annotations  # WARNING: remove this when debugging

from collections.abc import Sequence
from typing import Any
from typing import Callable

from dynaconf.utils.functional import Empty
from dynaconf.utils.functional import empty
from dynaconf.validator import Validator as BaseValidator

from .exceptions import ValidationError


class Validator:
    """Define an interface to generate a valid dynaconf.Validator.

    The `operations` are::

        eq: value == other
        ne: value != other
        gt: value > other
        lt: value < other
        gte: value >= other
        lte: value <= other
        is_type_of: isinstance(value, type)
        is_in:  value in sequence
        is_not_in: value not in sequence
        identity: value is other
        contains: contain value in
        not_contains: not contains value
        len_eq: len(value) == other
        len_ne: len(value) != other
        len_min: len(value) > other
        len_max: len(value) < other
        startswith: value.startswith(term)
        endswith:  value.endswith(term)
        not_startswith: not value.startswith(term)
        not_endswith:  not value.endswith(term)
        regex: pattern.match(value)
        not_regex: not pattern.match(value)
        condition: fn(value) is True
    """

    __slots__ = ()

    def __new__(
        cls,
        *,  # kw_only
        # Operations
        eq: Any = empty,
        ne: Any = empty,
        gt: Any = empty,
        lt: Any = empty,
        gte: Any = empty,
        lte: Any = empty,
        identity: Any = empty,
        is_in: Any = empty,
        is_not_in: Any = empty,
        contains: Any = empty,
        not_contains: Any = empty,
        len_eq: Any = empty,
        len_ne: Any = empty,
        len_min: Any = empty,
        len_max: Any = empty,
        startswith: Any = empty,
        endswith: Any = empty,
        not_startswith: Any = empty,
        not_endswith: Any = empty,
        regex: Any = empty,
        not_regex: Any = empty,
        condition: Callable[[Any], bool] | None | Empty = empty,
        # options
        env: str | Sequence[str] | None | Empty = empty,
        messages: dict[str, str] | None | Empty = empty,
        cast: Callable[[Any], Any] | None | Empty = empty,
        description: str | None | Empty = empty,
        items_validators: list[BaseValidator] | None = None,
        # To be implemented, a interface like this to generate a When Validator
        # when: When | None = empty,
    ):
        kwargs = locals()
        kwargs.pop("cls")
        return BaseValidator(
            **{k: v for k, v in kwargs.items() if v is not empty}
        )


class ItemsValidator:
    """Validates each internal item in a sequence or mapping.

    Validates all integers in a list are >= 10::

        field: Annotated[list[int], ItemsValidator(gte=10)]

    The same as above but reusing validators::

        min_value = Validator(gte=10)
        max_value = Validator(lte=100)
        field: Annotated[list[int], ItemsValidator(min_value, max_value)]

    Validates that values of the `port` key is not equal 5432::

        field: Annotated[dict[str, int], ItemsValidator("port", ne=5432)]

    Going down inside a dict of dict::

        field: Annotated[
            dict[str, dict[str, int]],
            ItemsValidator(
                "database",
                ItemsValidator("port, ne=5432)
            )
        ]

    For more complex cases the recommendations is to use `condition=function`::

        def my_value_is_valid(value) -> bool: ...

        field: Annotated[..., Validator(condition=my_value_is_valid)]

    """

    __slots__ = ()

    def __new__(
        cls,
        *args,
        # Operations
        eq: Any = empty,
        ne: Any = empty,
        gt: Any = empty,
        lt: Any = empty,
        gte: Any = empty,
        lte: Any = empty,
        identity: Any = empty,
        is_in: Any = empty,
        is_not_in: Any = empty,
        contains: Any = empty,
        not_contains: Any = empty,
        len_eq: Any = empty,
        len_ne: Any = empty,
        len_min: Any = empty,
        len_max: Any = empty,
        startswith: Any = empty,
        endswith: Any = empty,
        not_startswith: Any = empty,
        not_endswith: Any = empty,
        regex: Any = empty,
        not_regex: Any = empty,
        condition: Callable[[Any], bool] | None | Empty = empty,
        # options
        env: str | Sequence[str] | None | Empty = empty,
        messages: dict[str, str] | None | Empty = empty,
        cast: Callable[[Any], Any] | None | Empty = empty,
        description: str | None | Empty = empty,
        items_validators: list[BaseValidator] | None = None,
        # To be implemented, a interface like this to generate a When Validator
        # when: When | None = empty,
    ):
        kwargs = locals()
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if v is not empty and k not in ("cls", "args", "items_validators")
        }
        if items_validators:
            kwargs["items_validators"] = items_validators

        validators = [arg for arg in args if isinstance(arg, BaseValidator)]
        if kwargs:
            names = [arg for arg in args if isinstance(args, str)]
            validators.append(BaseValidator(*names, **kwargs))
        return BaseValidator(items_validators=validators)


# Utilities
# Inspired by the module annotated_types


class Not(BaseValidator):
    """Inverts a Validator

    field: Annotated[int, Not(Eq(10))]
    # actually the same as
    field: Annotated[int, Ne(10)]
    # but for SpecifiedOperations is much more semantic
    field: Annotated[str, Not(IsUrl())]
    """

    _validator: BaseValidator

    def __init__(self, validator: BaseValidator):
        self._validator = validator

    def validate(self, *args, **kwargs):
        self._validator.names = self.names
        try:
            # triggers validation of wrapped validator
            self._validator.validate(*args, **kwargs)
        except ValidationError:
            # If it fails then it is ok!
            return

        # If not fails, than it is an error
        raise ValidationError(f"Not({self._validator}) failed.")

    def __getattr__(self, name):
        return getattr(self._validator, name)


# Generic Validation Aliases


class GenericOperation:
    """Base to create aliased Validator with generic parametrized operation.

    This class exists mainly to allow creation of semantic named validators.

    Usage::

      class NoWayItIs(GenericOperation):
          op_name = "eq"

      field: Annotated[T, NoWatItIs("pineapple")]

    Which is equivalent to::

      field: Annotatted[T, Validator(ne="pineapple")]

    Non parametrized alternative would be::

      NoWayItIsPineApple = Validator(ne="pineapple")
      field: Annotated[T, NoWayItIsPineApple]

    """

    def __new__(cls, op_value):
        kwargs = {cls.op_name: op_value}
        return Validator(**kwargs)


class Eq(GenericOperation):
    """Eq(x) -> Validator(eq=x)"""

    op_name = "eq"


class Ne(GenericOperation):
    """Ne(x) -> Validator(ne=x)"""

    op_name = "ne"


class Gt(GenericOperation):
    """Gt(x) -> Validator(gt=x)"""

    op_name = "gt"


class Lt(GenericOperation):
    """Lt(x) -> Validator(lt=x)"""

    op_name = "lt"


class Gte(GenericOperation):
    """Gte(x) -> Validator(gte=x)"""

    op_name = "gte"


class Lte(GenericOperation):
    """Lte(x) -> Validator(lte=x)"""

    op_name = "lte"


class Id(GenericOperation):
    """Id(x) -> Validator(identity=x)"""

    op_name = "identity"


class In(GenericOperation):
    """In(x) -> Validator(is_in=x)"""

    op_name = "is_in"


class NotIn(GenericOperation):
    """NotIn(x) -> Validator(is_not_in=x)"""

    op_name = "is_not_in"


class Contains(GenericOperation):
    """Contains(x) -> Validator(contains=x)"""

    op_name = "contains"


class NotContains(GenericOperation):
    """NotContains(x) -> Validator(not_contains=x)"""

    op_name = "not_contains"


class LenEq(GenericOperation):
    """LenEq(x) -> Validator(len_eq=x)"""

    op_name = "len_eq"


class LenNe(GenericOperation):
    """LenNe(x) -> Validator(len_ne=x)"""

    op_name = "len_ne"


class LenMin(GenericOperation):
    """LenMin(x) -> Validator(len_min=x)"""

    op_name = "len_min"


class LenMax(GenericOperation):
    """LenMax(x) -> Validator(len_max=x)"""

    op_name = "len_max"


class Starts(GenericOperation):
    """Starts(x) -> Validator(startswith=x)"""

    op_name = "startswith"


class Ends(GenericOperation):
    """Ends(x) -> Validator(endswith=x)"""

    op_name = "endswith"


class NotStarts(GenericOperation):
    """NotStarts(x) -> Validator(not_startswith=x)"""

    op_name = "not_startswith"


class NotEnds(GenericOperation):
    """NotEnds(x) -> Validator(not_endswith=x)"""

    op_name = "not_endswith"


class Regex(GenericOperation):
    """Regex(x) -> Validator(regex=x)"""

    op_name = "regex"


class NotRegex(GenericOperation):
    """NotRegex(x) -> Validator(not_regex=x)"""

    op_name = "not_regex"


class Condition(GenericOperation):
    """Condition(x) -> Validator(condition=x)"""

    op_name = "condition"


# Custom Validation Aliases
# The aliases defined here are mostly examples
# users can create their own aliases for domain specific validation.


class CustomOperation:
    """Base to create custom non-parametrized operations.

    This base class is useful when the operation and parameters are constant.

    Usage::

        class IsAFruitILike(CustomOperation):
            op_name = "is_in"
            op_value = ["banana", "apple", "lemon", "orange"]

            fruit: Annotated[str, IsAFruitILike()]  # callable

    Which is equivalent to::

       IsAFruitILike = Validator(is_in=["banana", "apple", "lemon", "orange"])
       fruit: Annotated[str, IsAFruitILike]  # not callable

    However simply assigning the validator to a variable doesnt allow for
    inheritance and doesn't create a callable object, being a callable object
    is useful to keep the possibility to accept arguments if needed without
    breaking compatibility.
    """

    def __new__(cls):
        kwargs = {cls.op_name: cls.op_value}
        return Validator(**kwargs)


class IsUrl(CustomOperation):
    """IsUrl(x) -> Validator(regex=url_pattern)"""

    op_name = "regex"
    op_value = (
        r"((http|https)://)"  # Match the protocol (http or https) required
        r"(www\.)?"  # Match 'www.' optionally
        r"[\w.-]+"  # Match the domain name
        r"\.[a-z]{2,}"  # Match the top-level domain
        r"(/[^\s]*)?"  # Match the path (everything after the domain name)
    )


class IsConnectionString(CustomOperation):
    op_name = "regex"
    op_value = (
        r"^(?P<scheme>postgresql|mysql|sqlite):\/\/"
        r"(?:(?P<user>[^:]+):"
        r"(?P<password>[^@]+)@)?"
        r"(?P<host>[^:\/]+)?"
        r"(?::(?P<port>\d+))?"
        r"\/(?P<path>[^\s]+)$"
    )


class IsSemVer(CustomOperation):
    op_name = "regex"
    op_value = (
        r"^(\d+)\.(\d+)\.(\d+)"
        r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
        r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    )


class PositiveInt(CustomOperation):
    op_name = "gt"
    op_value = 0


class NegativeInt(CustomOperation):
    op_name = "lt"
    op_value = 0
