# coding: utf-8
from dynaconf import LazySettings, Validator

settings = LazySettings(
    ENV_FOR_DYNACONF='EXAMPLE',
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
    Validator('PORT', must_exist=True, ne=8000, when=Validator('MYSQL_HOST',
                                                               eq='localhost'))
)

settings.validators.validate()
