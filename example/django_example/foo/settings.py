import os

"""
NOTE: All the variables defined here can be moved to separate file
see settings.toml [default] section.
"""

# DJANGO common settings variables:

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'


# HERE STARTS DYNACONF PATCHING
import os  # noqa
import sys  # noqa
import dynaconf  # noqa
_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dynaconf.default_settings.AUTO_LOAD_DOTENV = False  # noqa
dynaconf.default_settings.start_dotenv(root_path=_ROOT_PATH)

# For a list of config keys see:
# https://dynaconf.readthedocs.io/en/latest/guides/configuration.html
# Those keys can also be set as environment variables.
lazy_settings = dynaconf.LazySettings(

    # Configure this instance of Dynaconf
    GLOBAL_ENV_FOR_DYNACONF='DJANGO',
    ENV_FOR_DYNACONF=os.environ.get('DJANGO_ENV', 'DEVELOPMENT'),
    ROOT_PATH_FOR_DYNACONF=_ROOT_PATH,

    # Extra useful options
    # SETTINGS_MODULE_FOR_DYNACONF='/etc/myprogram/settings.toml'
    # INCLUDES_FOR_DYNACONF=['/etc/myprogram/plugins/*'],

    # Then rebind all settings defined above on this settings.py file.
    **{k: v for k, v in locals().items() if k.isupper()}

)

# This makes django check happy because all settings is provided
for setting_name, setting_value in lazy_settings._store.items():
    setattr(sys.modules[__name__], setting_name.upper(), setting_value)

# This import makes `django.conf.settings` to behave dynamically
from dynaconf.contrib import django_dynaconf_v2  # noqa
django_dynaconf_v2.load(lazy_settings)
# HERE ENDS DYNACONF PATCHING
