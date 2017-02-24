# coding: utf-8
from dynaconf import LazySettings, Validator, Transformator

settings = LazySettings(
    ENVVAR_FOR_DYNACONF="EXAMPLE_SETTINGS_MODULE",
    DYNACONF_NAMESPACE='EXAMPLE',
    silent=True
)

settings.validators.register(
    Validator('VERSION', 'AGE', 'NAME', defined=True),
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
        namespace='DEVELOPMENT',
        ne='Trump',
    ),
    Validator(
        'SALARY',
        lt=1000000,
        gt=1000
    ),
    Validator(
        'DEV_SERVERS',
        defined=True,
        is_type_of=(list, tuple)
    ),
    Validator(
        'MYSQL_HOST', namespace='DEVELOPMENT', is_in=settings.DEV_SERVERS
    ),
    Validator(
        'MYSQL_HOST', namespace='PRODUCTION', is_not_in=settings.DEV_SERVERS
    ),
    Validator('NAME', condition=lambda x: x in ('BRUNO', 'MIKE')),
    Validator(
        'IMAGE_1', 'IMAGE_2',
        namespace='development',
        defined=True,
        when=Validator('BASE_IMAGE', defined=True,
                       namespace=settings.DYNACONF_NAMESPACE)
    ),
    Validator(
        'IMAGE_4', 'IMAGE_5',
        namespace=('development', 'production'),
        defined=True, when=Validator('BASE_IMAGE', defined=False,
                                     namespace=settings.DYNACONF_NAMESPACE)
    ),
    Validator('PORT', defined=True, ne=8000, when=Validator('MYSQL_HOST',
                                                            eq='localhost'))
)

settings.validators.validate()

settings.transformators.register(
    Transformator('NAME', using=lambda x: x.replace('n', 'x'))
)
