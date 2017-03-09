
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='dynaconf',
    version="0.4.2",
    url='https://github.com/rochacbruno/dynaconf',
    license='MIT',
    author="Bruno Rocha",
    author_email="rochacbruno@gmail.com",
    description='The dynamic configurator for your Python Project',
    long_description="""dynaconf is an OSM (Object Settings Mapper) it can
    read settings variables from a set of different data stores such as python
    settings files, environment variables, redis, memcached, ini files,
    json files, yaml files and you can customize dynaconf loaders to read
    from wherever you want
    """,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['six'],
    tests_require=[
        "pytest",
        "pytest-cov",
        "flake8",
        "pep8-naming",
        "flake8-debugger",
        "flake8-print",
        "flake8-todo",
        "radon"
    ],
    extras_require={
        "redis": ['redis'],
        "yaml": ['PyYAML'],
        "toml": ['toml'],
        "all": ['redis', 'PyYAML', 'toml'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
