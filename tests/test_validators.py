import pytest
from dynaconf import LazySettings, Validator, ValidationError


TOML = """
[default]
EXAMPLE = true
MYSQL_HOST = 'localhost'
DEV_SERVERS = ['127.0.0.1', 'localhost', 'development.com']
VERSION = 1
AGE = 15
NAME = 'BRUNO'
PORT = 8001
BASE_IMAGE = 'bla'
PRESIDENT = 'Lula'
PROJECT = 'hello_world'
SALARY = 2000
WORKS = 'validator'

[development]
MYSQL_HOST = 'development.com'
VERSION = 1
AGE = 15
NAME = 'MIKE'
IMAGE_1 = 'aaa'
IMAGE_2 = 'bbb'
IMAGE_4 = 'a'
IMAGE_5 = 'b'

[production]
MYSQL_HOST = 'production.com'
VERSION = 1
AGE = 15
NAME = 'MIKE'
IMAGE_4 = 'a'
IMAGE_5 = 'b'

[global]
MYSQL_PASSWD = "SuperSecret"
TESTVALUE = "value"
"""


def test_validators(tmpdir):

    tmpfile = tmpdir.join('settings.toml')
    tmpfile.write(TOML)

    settings = LazySettings(
        ENV_FOR_DYNACONF='EXAMPLE',
        SETTINGS_MODULE_FOR_DYNACONF=str(tmpfile),
        silent=True
    )

    settings.validators.register(
        Validator('VERSION', 'AGE', 'NAME', must_exist=True),
        Validator(
            'AGE',
            lte=30,
            gte=10,
        ),
        Validator(
            'PROJECT',
            eq='hello_world',
        ),
        Validator(
            'PRESIDENT',
            env='DEVELOPMENT',
            ne='Trump',
        ),
        Validator(
            'SALARY',
            lt=1000000,
            gt=1000
        ),
        Validator(
            'DEV_SERVERS',
            must_exist=True,
            is_type_of=(list, tuple)
        ),
        Validator(
            'MYSQL_HOST', env='DEVELOPMENT', is_in=settings.DEV_SERVERS
        ),
        Validator(
            'MYSQL_HOST', env='PRODUCTION', is_not_in=settings.DEV_SERVERS
        ),
        Validator('NAME', condition=lambda x: x in ('BRUNO', 'MIKE')),
        Validator(
            'IMAGE_1', 'IMAGE_2',
            env='development',
            must_exist=True,
            when=Validator('BASE_IMAGE', must_exist=True,
                           env=settings.ENV_FOR_DYNACONF)
        ),
        Validator(
            'IMAGE_4', 'IMAGE_5',
            env=('development', 'production'),
            must_exist=True, when=Validator(
                'BASE_IMAGE', must_exist=False,
                env=settings.ENV_FOR_DYNACONF
            )
        ),
        Validator('PORT',
                  must_exist=True, ne=8000,
                  when=Validator('MYSQL_HOST', eq='localhost'))
    )

    assert settings.validators.validate() is None

    settings.validators.register(
        Validator('TESTVALUEZZ', env='development'),
        Validator('TESTVALUE', eq='hello_world')
    )

    with pytest.raises(ValidationError):
        settings.validators.validate()

    with pytest.raises(TypeError):
        Validator('A', condition=1)

    with pytest.raises(TypeError):
        Validator('A', when=1)


@pytest.mark.parametrize(
    'validator_instance',
    [
        Validator('TESTVALUE', eq='hello_world'),
        Validator('PROJECT', condition=lambda x: False, env='development'),
        Validator('TESTVALUEZZ', must_exist=True),

    ]
)
def test_validation_error(validator_instance, tmpdir):
    tmpfile = tmpdir.join('settings.toml')
    tmpfile.write(TOML)

    settings = LazySettings(
        ENV_FOR_DYNACONF='EXAMPLE',
        SETTINGS_MODULE_FOR_DYNACONF=str(tmpfile),
        silent=True
    )
    settings.validators.register(validator_instance)
    with pytest.raises(ValidationError):
        settings.validators.validate()
