from __future__ import annotations

import inspect
from collections import defaultdict
from itertools import chain
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from dynaconf import validator_conditions
from dynaconf.utils import ensure_a_list
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import jinja_env


EQUALITY_ATTRS = (
    "names",
    "must_exist",
    "when",
    "condition",
    "operations",
    "envs",
)


class ValidationError(Exception):
    pass


class Validator:
    """Validators are conditions attached to settings variables names
    or patterns::

        Validator('MESSAGE', must_exist=True, eq='Hello World')

    The above ensure MESSAGE is available in default env and
    is equal to 'Hello World'

    `names` are a one (or more) names or patterns::

        Validator('NAME')
        Validator('NAME', 'OTHER_NAME', 'EVEN_OTHER')
        Validator(r'^NAME', r'OTHER./*')

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
        cont: contain value in
        len_eq: len(value) == other
        len_ne: len(value) != other
        len_min: len(value) > other
        len_max: len(value) < other

    `env` is which env to be checked, can be a list or
    default is used.

    `when` holds a validator and its return decides if validator runs or not::

        Validator('NAME', must_exist=True, when=Validator('OTHER', eq=2))
        # NAME is required only if OTHER eq to 2
        # When the very first thing to be performed when passed.
        # if no env is passed to `when` it is inherited

    `must_exist` is alias to `required` requirement. (executed after when)::

       settings.get(value, empty) returns non empty

    condition is a callable to be executed and return boolean::

       Validator('NAME', condition=lambda x: x == 1)
       # it is executed before operations.

    """

    default_messages = MappingProxyType(
        {
            "must_exist_true": "{name} is required in env {env}",
            "must_exist_false": "{name} cannot exists in env {env}",
            "condition": "{name} invalid for {function}({value}) in env {env}",
            "operations": (
                "{name} must {operation} {op_value} "
                "but it is {value} in env {env}"
            ),
            "combined": "combined validators failed {errors}",
            "expr": "Expression {expr} failed for {name}",
        }
    )

    def __init__(
        self,
        *names: str,
        must_exist: Optional[bool] = None,
        required: Optional[bool] = None,  # alias for `must_exist`
        condition: Optional[Callable[[Any], bool]] = None,
        when: Optional[Validator] = None,
        env: Optional[Union[str, Sequence[str]]] = None,
        messages: Optional[Dict[str, str]] = None,
        cast: Optional[Callable[[Any], Any]] = None,
        default: Optional[Union[Any, Callable[[Any, Validator], Any]]] = empty,
        description: Optional[str] = None,
        expr: Optional[str] = None,
        **operations: Any,
    ) -> None:
        # Copy immutable MappingProxyType as a mutable dict
        self.messages = dict(self.default_messages)
        if messages:
            self.messages.update(messages)

        if when is not None and not isinstance(when, Validator):
            raise TypeError("when must be Validator instance")

        if condition is not None and not callable(condition):
            raise TypeError("condition must be callable")

        self.names = names
        self.must_exist = must_exist if must_exist is not None else required
        self.condition = condition
        self.when = when
        self.cast = cast or (lambda value: value)
        self.operations = operations
        self.default = default
        self.description = description
        self.expr = expr
        self.envs: Optional[Sequence[str]] = None

        if isinstance(env, str):
            self.envs = [env]
        elif isinstance(env, (list, tuple)):
            self.envs = env

    def __or__(self, other: Validator) -> CombinedValidator:
        return OrValidator(self, other, description=self.description)

    def __and__(self, other: Validator) -> CombinedValidator:
        return AndValidator(self, other, description=self.description)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True

        if type(self).__name__ != type(other).__name__:
            return False

        identical_attrs = (
            getattr(self, attr) == getattr(other, attr)
            for attr in EQUALITY_ATTRS
        )
        if all(identical_attrs):
            return True

        return False

    def validate(
        self,
        settings: Any,
        only: Optional[Union[str, Sequence]] = None,
        exclude: Optional[Union[str, Sequence]] = None,
    ) -> None:
        """Raise ValidationError if invalid"""
        # If only or exclude are not set, this value always passes startswith
        only = ensure_a_list(only or [""])
        if only and not isinstance(only[0], str):
            raise ValueError("'only' must be a string or list of strings.")

        exclude = ensure_a_list(exclude)
        if exclude and not isinstance(exclude[0], str):
            raise ValueError("'exclude' must be a string or list of strings.")

        if self.envs is None:
            self.envs = [settings.current_env]

        if self.when is not None:
            try:
                # inherit env if not defined
                if self.when.envs is None:
                    self.when.envs = self.envs

                self.when.validate(settings, only=only, exclude=exclude)
            except ValidationError:
                # if when is invalid, return canceling validation flow
                return

        # If only using current_env, skip using_env decoration (reload)
        if (
            len(self.envs) == 1
            and self.envs[0].upper() == settings.current_env.upper()
        ):
            self._validate_items(
                settings, settings.current_env, only=only, exclude=exclude
            )
            return

        for env in self.envs:
            self._validate_items(
                settings.from_env(env), only=only, exclude=exclude
            )

    def _validate_items(
        self,
        settings: Any,
        env: Optional[str] = None,
        only: Optional[Union[str, Sequence]] = None,
        exclude: Optional[Union[str, Sequence]] = None,
    ) -> None:
        env = env or settings.current_env
        for name in self.names:
            # Skip if only is set and name isn't in the only list
            if only and not any(name.startswith(sub) for sub in only):
                continue

            # Skip if exclude is set and name is in the exclude list
            if exclude and any(name.startswith(sub) for sub in exclude):
                continue

            if self.default is not empty:
                # This was made to keep backward compatibility
                # default can accept a callable that receives
                # this or settings pointing to the settings instance
                # some current users shorted to `st` and `va`
                if callable(self.default):
                    default_kwargs = {}
                    default_params = inspect.signature(self.default).parameters
                    if "this" in default_params:
                        default_kwargs["this"] = settings
                    elif "settings" in default_params:
                        default_kwargs["settings"] = settings
                    elif "st" in default_params:
                        default_kwargs["st"] = settings

                    if "validator" in default_params:
                        default_kwargs["validator"] = self
                    elif "va" in default_params:
                        default_kwargs["va"] = self

                    default_value = self.default(  # type: ignore
                        **default_kwargs
                    )
                else:
                    default_value = self.default
            else:
                default_value = empty

            value = self.cast(settings.setdefault(name, default_value))

            # is name required but not exists?
            if self.must_exist is True and value is empty:
                raise ValidationError(
                    self.messages["must_exist_true"].format(name=name, env=env)
                )

            if self.must_exist is False and value is not empty:
                raise ValidationError(
                    self.messages["must_exist_false"].format(
                        name=name, env=env
                    )
                )

            if self.must_exist in (False, None) and value is empty:
                continue

            # is there a callable condition?
            if self.condition is not None:
                # This was made to keep backward compatibility
                # condition can accept a callable that receives
                # this or settings pointing to the settings instance
                # some current users shorted to `st`
                # also the condition value has been shorted as `x`
                condition_kwargs = {}
                condition_params = inspect.signature(self.condition).parameters

                if "value" in condition_params:
                    condition_kwargs["value"] = value
                else:
                    for param in condition_params:
                        if param not in ("this", "settings", "st"):
                            condition_kwargs[param] = value  # handle `x` case

                if "this" in condition_params:
                    condition_kwargs["this"] = settings
                elif "settings" in condition_params:
                    condition_kwargs["settings"] = settings
                elif "st" in condition_params:
                    condition_kwargs["st"] = settings

                if not self.condition(**condition_kwargs):  # type: ignore
                    raise ValidationError(
                        self.messages["condition"].format(
                            name=name,
                            function=self.condition.__name__,
                            value=value,
                            env=env,
                        )
                    )

            # is there a Jinja Expression?
            if self.expr is not None:
                result = jinja_env.compile_expression(self.expr)(
                    this=settings,
                    value=value,
                )
                if not result:
                    raise ValidationError(
                        self.messages["expr"].format(name=name, expr=self.expr)
                    )

            # operations
            for op_name, op_value in self.operations.items():
                op_function = getattr(validator_conditions, op_name)
                if not op_function(value, op_value):
                    raise ValidationError(
                        self.messages["operations"].format(
                            name=name,
                            operation=op_function.__name__,
                            op_value=op_value,
                            value=value,
                            env=env,
                        )
                    )


class CombinedValidator(Validator):
    def __init__(
        self,
        validator_a: Validator,
        validator_b: Validator,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Takes 2 validators and combines the validation"""
        self.validators = (validator_a, validator_b)
        super().__init__(*args, **kwargs)
        for attr in EQUALITY_ATTRS:
            if not getattr(self, attr, None):
                value = tuple(
                    getattr(validator, attr) for validator in self.validators
                )
                setattr(self, attr, value)

    def validate(
        self,
        settings: Any,
        only: Optional[Union[str, Sequence]] = None,
        exclude: Optional[Union[str, Sequence]] = None,
    ) -> None:  # pragma: no cover
        raise NotImplementedError(
            "subclasses OrValidator or AndValidator implements this method"
        )


class OrValidator(CombinedValidator):
    """Evaluates on Validator() | Validator()"""

    def validate(
        self,
        settings: Any,
        only: Optional[Union[str, Sequence]] = None,
        exclude: Optional[Union[str, Sequence]] = None,
    ) -> None:
        """Ensure at least one of the validators are valid"""
        errors = []
        for validator in self.validators:
            try:
                validator.validate(settings, only=only, exclude=exclude)
            except ValidationError as e:
                errors.append(e)
                continue
            else:
                return

        raise ValidationError(
            self.messages["combined"].format(
                errors=" or ".join(
                    str(e).replace("combined validators failed ", "")
                    for e in errors
                )
            )
        )


class AndValidator(CombinedValidator):
    """Evaluates on Validator() & Validator()"""

    def validate(
        self,
        settings: Any,
        only: Optional[Union[str, Sequence]] = None,
        exclude: Optional[Union[str, Sequence]] = None,
    ) -> None:
        """Ensure both the validators are valid"""
        errors = []
        for validator in self.validators:
            try:
                validator.validate(settings, only=only, exclude=exclude)
            except ValidationError as e:
                errors.append(e)
                continue

        if errors:
            raise ValidationError(
                self.messages["combined"].format(
                    errors=" and ".join(
                        str(e).replace("combined validators failed ", "")
                        for e in errors
                    )
                )
            )


class ValidatorList(list):
    def __init__(
        self,
        settings: Any,
        validators: Optional[Sequence[Validator]] = None,
        *args: Validator,
        **kwargs: Any,
    ) -> None:
        if isinstance(validators, (list, tuple)):
            args = list(args) + list(validators)  # type: ignore
        self._only = kwargs.pop("validate_only", None)
        self._exclude = kwargs.pop("validate_exclude", None)
        super(ValidatorList, self).__init__(args, **kwargs)  # type: ignore
        self.settings = settings

    def register(self, *args: Validator, **kwargs: Validator):
        validators: List[Validator] = list(
            chain.from_iterable(kwargs.values())  # type: ignore
        )
        validators.extend(args)
        for validator in validators:
            if validator and validator not in self:
                self.append(validator)

    def descriptions(
        self, flat: bool = False
    ) -> Dict[str, Union[str, List[str]]]:

        if flat:
            descriptions: Dict[str, Union[str, List[str]]] = {}
        else:
            descriptions = defaultdict(list)

        for validator in self:
            for name in validator.names:
                if isinstance(name, tuple) and len(name) > 0:
                    name = name[0]
                if flat:
                    descriptions.setdefault(name, validator.description)
                else:
                    descriptions[name].append(  # type: ignore
                        validator.description
                    )
        return descriptions

    def validate(
        self,
        only: Optional[Union[str, Sequence]] = None,
        exclude: Optional[Union[str, Sequence]] = None,
    ) -> None:
        for validator in self:
            validator.validate(self.settings, only=only, exclude=exclude)
