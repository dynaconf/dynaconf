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
ZERO = 0
FALSE = false

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
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
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
                  when=Validator('MYSQL_HOST', eq='localhost')),
        #
        Validator(
            'ZERO',
            is_type_of=int,
            eq=0,
        ),
        Validator(
            'FALSE',
            is_type_of=bool,
            eq=False,
        ),
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


def test_dotted_validators(settings):

    settings.set(
        'PARAMS',
        {
            'PASSWORD': 'secret',
            'SSL': {
                'CONTEXT': 'SECURE',
                'ENABLED': True
            },
        }
    )

    settings.validators.register(
        Validator('PARAMS', must_exist=True,  is_type_of=dict),
        Validator('PARAMS.PASSWORD', must_exist=True, is_type_of=str),
        Validator('PARAMS.SSL', must_exist=True, is_type_of=dict),
        Validator('PARAMS.SSL.ENABLED', must_exist=True, is_type_of=bool),
        Validator('PARAMS.NONEXISTENT', must_exist=False, is_type_of=str)
    )

    assert settings.validators.validate() is None


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
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
        silent=True
    )
    settings.validators.register(validator_instance)
    with pytest.raises(ValidationError):
        settings.validators.validate()


def test_no_reload_on_single_env(tmpdir, mocker):
    tmpfile = tmpdir.join('settings.toml')
    tmpfile.write(TOML)

    same_env_validator = Validator(
        'VERSION', is_type_of=int, env='development')
    other_env_validator = Validator(
        'NAME', must_exist=True, env='production')

    settings = LazySettings(
        ENV_FOR_DYNACONF='DEVELOPMENt',
        SETTINGS_FILE_FOR_DYNACONF=str(tmpfile),
    )
    using_env = mocker.patch.object(settings, "using_env")

    settings.validators.register(same_env_validator)
    settings.validators.validate()
    using_env.assert_not_called()

    settings.validators.register(other_env_validator)
    settings.validators.validate()
    using_env.assert_any_call('production')
    assert using_env.call_count == 1
