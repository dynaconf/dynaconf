from dynaconf import Dynaconf
from dynaconf import Validator
from dynaconf.utils.functional import empty
from dynaconf.utils.parse_conf import Lazy


def test_lazy_error(tmp_path):
    def my_lazy_function(value, **context):
        """
        value: Default value passed to the validator, defaults to `empty`
        context: A dictionary containing
                env: All the environment variables
                this: The settings instance
        """
        raise RuntimeError("Should never be hit.")
        return "When the first value is accessed, then the my_lazy_function will be called"

    settings = Dynaconf(
        validators=[
            Validator(
                "MYSQL_HOST",
                eq="development.com",
                default="development.com",
            ),
            Validator(
                "MYSQL_HOST",
                ne="development.com",
                env="PRODUCTION",
                default="development.comp",
            ),
            Validator("FOO", default=Lazy(empty, formatter=my_lazy_function)),
        ]
    )
    assert settings.MYSQL_HOST
