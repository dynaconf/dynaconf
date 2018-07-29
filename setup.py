
import io
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


def read(*names, **kwargs):
    """Read a file."""
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read().strip()


setup(
    name='dynaconf',
    version=read('dynaconf', 'VERSION'),
    url='https://github.com/rochacbruno/dynaconf',
    license='MIT',
    author="Bruno Rocha",
    author_email="rochacbruno@gmail.com",
    description='The dynamic configurator for your Python Project',
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    packages=find_packages(
        exclude=['tests', 'tests.*', 'example', 'example.*']
    ),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['six', 'python-box', 'python-dotenv', 'toml', 'click'],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-xdist",
        "flake8",
        "pep8-naming",
        "flake8-debugger",
        "flake8-print",
        "flake8-todo",
        "radon",
        "flask>=0.12",
        "python-dotenv",
        "toml",
        "codecov"
    ],
    extras_require={
        "redis": ['redis'],
        "vault": ['hvac'],
        "yaml": ['PyYAML'],
        "toml": ['toml'],
        "ini": ['configobj'],
        "configobj": ['configobj'],
        "all": ['redis', 'PyYAML', 'configobj', 'hvac'],
    },
    entry_points={
        'console_scripts': [
            'dynaconf=dynaconf.cli:main'
        ]
    },
    setup_requires=['setuptools>=38.6.0'],
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Django',
          'Framework :: Flask',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: OS Independent',
      ],
)
