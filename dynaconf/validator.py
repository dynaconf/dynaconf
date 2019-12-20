from types import MappingProxyType

from dynaconf import validator_conditions  # noqa


class ValidationError(Exception):
    pass


class Validator(object):
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

    `env` is which env to be checked, can be a list or
    default is used.

    `when` holds a validator and its return decides if validator runs or not::

        Validator('NAME', must_exist=True, when=Validator('OTHER', eq=2))
        # NAME is required only if OTHER eq to 2
        # When the very first thing to be performed when passed.
        # if no env is passed to `when` it is inherited

    `must_exist` is `exists` requirement. (executed after when)::

       settings.exists(value)

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
        }
    )

    def __init__(
        self,
        *names,
        must_exist=None,
        condition=None,
        when=None,
        env=None,
        messages=None,
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
        self.must_exist = must_exist
        self.condition = condition
        self.when = when
        self.operations = operations

        if isinstance(env, str):
            self.envs = [env]
        elif isinstance(env, (list, tuple)):
            self.envs = env
        else:
            self.envs = None

    def __eq__(self, other):
        if self is other:
            return True

        identical_attrs = (
            getattr(self, attr) == getattr(other, attr)
            for attr in (
                "names",
                "must_exist",
                "when",
                "condition",
                "operations",
                "envs",
            )
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
            exists = settings.exists(name)

            # is name required but not exists?
            if self.must_exist is True and not exists:
                raise ValidationError(
                    self.messages["must_exist_true"].format(name=name, env=env)
                )
            elif self.must_exist is False and exists:
                raise ValidationError(
                    self.messages["must_exist_false"].format(
                        name=name, env=env
                    )
                )

            # if not exists and not required cancel validation flow
            if not exists:
                return

            value = settings[name]

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


class ValidatorList(list):
    def __init__(self, settings, *args, **kwargs):
        super(ValidatorList, self).__init__(*args, **kwargs)
        self.settings = settings

    def register(self, *args):
        for validator in args:
            if validator not in self:
                self.append(validator)

    def validate(self):
        for validator in self:
            validator.validate(self.settings)
