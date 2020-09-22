from itertools import chain
from types import MappingProxyType

from dynaconf import validator_conditions  # noqa
from dynaconf.utils.functional import empty


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
        }
    )

    def __init__(
        self,
        *names,
        must_exist=None,
        required=None,  # this is alias for `must_exist`
        condition=None,
        when=None,
        env=None,
        messages=None,
        cast=None,
        default=empty,  # Literal value or a callable
        **operations
    ):
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

        if isinstance(env, str):
            self.envs = [env]
        elif isinstance(env, (list, tuple)):
            self.envs = env
        else:
            self.envs = None

    def __or__(self, other):
        return OrValidator(self, other)

    def __and__(self, other):
        return AndValidator(self, other)

    def __eq__(self, other):
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

    def validate(self, settings):
        """Raise ValidationError if invalid"""

        if self.envs is None:
            self.envs = [settings.current_env]

        if self.when is not None:
            try:
                # inherit env if not defined
                if self.when.envs is None:
                    self.when.envs = self.envs

                self.when.validate(settings)
            except ValidationError:
                # if when is invalid, return canceling validation flow
                return

        # If only using current_env, skip using_env decoration (reload)
        if (
            len(self.envs) == 1
            and self.envs[0].upper() == settings.current_env.upper()
        ):
            self._validate_items(settings, settings.current_env)
            return

        for env in self.envs:
            self._validate_items(settings.from_env(env))

    def _validate_items(self, settings, env=None):
        env = env or settings.current_env
        for name in self.names:
            if self.default is not empty:
                default_value = (
                    self.default(settings, self)
                    if callable(self.default)
                    else self.default
                )
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
                if not self.condition(value):
                    raise ValidationError(
                        self.messages["condition"].format(
                            name=name,
                            function=self.condition.__name__,
                            value=value,
                            env=env,
                        )
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
    def __init__(self, validator_a, validator_b, *args, **kwargs):
        """Takes 2 validators and combines the validation"""
        self.validators = (validator_a, validator_b)
        super().__init__(*args, **kwargs)
        for attr in EQUALITY_ATTRS:
            if not getattr(self, attr, None):
                value = tuple(
                    getattr(validator, attr) for validator in self.validators
                )
                setattr(self, attr, value)

    def validate(self, settings):  # pragma: no cover
        raise NotImplementedError(
            "subclasses OrValidator or AndValidator implements this method"
        )


class OrValidator(CombinedValidator):
    """Evaluates on Validator() | Validator()"""

    def validate(self, settings):
        """Ensure at least one of the validators are valid"""
        errors = []
        for validator in self.validators:
            try:
                validator.validate(settings)
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

    def validate(self, settings):
        """Ensure both the validators are valid"""
        errors = []
        for validator in self.validators:
            try:
                validator.validate(settings)
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
    def __init__(self, settings, validators=None, *args, **kwargs):
        if isinstance(validators, (list, tuple)):
            args = list(args) + list(validators)
        super(ValidatorList, self).__init__(args, **kwargs)
        self.settings = settings

    def register(self, *args, **kwargs):
        validators = list(chain.from_iterable(kwargs.values()))
        validators.extend(args)
        for validator in validators:
            if validator and validator not in self:
                self.append(validator)

    def validate(self):
        for validator in self:
            validator.validate(self.settings)
