# coding: utf-8
from dynaconf import validator_conditions


class ValidationError(Exception):
    pass


class Validator(object):
    """Validators are conditions attached to settings variables names
    or patterns::

        Validator('MESSAGE', defined=True, eq='Hello World')

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

        Validator('NAME', defined=True, when=Validator('OTHER', eq=2))
        # NAME is required only if OTHER eq to 2
        # When the very first thing to be performed when passed.
        # if no env is passed to `when` it is inherited

    `must_exist` is `exists` requirement. (executed after when)::

       settings.exists(value)

    condition is a callable to be executed and return boolean::

       Validator('NAME', condition=lambda x: x == 1)
       # it is executed before operations.

    """
    def __init__(
            self,
            *names,
            must_exist=None,
            condition=None,
            when=None,
            env=None,
            **operations):

        if when is not None and not isinstance(when, Validator):
            raise TypeError('when must be Validator instance')

        if condition is not None and not callable(condition):
            raise TypeError('condition must be callable')

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

        for env in self.envs:
            with settings.using_env(env):
                for name in self.names:
                    exists = settings.exists(name)

                    # is name required but not exists?
                    if self.must_exist is True and not exists:
                        raise ValidationError(
                            '{0} is required in env {1}'.format(
                                name, env
                            )
                        )
                    elif self.must_exist is False and exists:
                        raise ValidationError(
                            '{0} cannot exists in env {1}'.format(
                                name, env
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
                                '{0} invalid for {1}({2}) '
                                'in env {3}'.format(
                                    name, self.condition.__name__,
                                    value, env
                                )
                            )

                    # operations
                    for op_name, op_value in self.operations.items():
                        op_function = getattr(validator_conditions, op_name)
                        if not op_function(value, op_value):
                            raise ValidationError(
                                '{0} must {1} {2} but it is {3} '
                                'in env {4}'.format(
                                    name, op_function.__name__,
                                    op_value, value, env
                                )
                            )


class ValidatorList(list):

    def __init__(self, settings, *args, **kwargs):
        super(ValidatorList, self).__init__(*args, **kwargs)
        self.settings = settings

    def register(self, *args):
        self.extend(args)

    def validate(self):
        for validator in self:
            validator.validate(self.settings)
