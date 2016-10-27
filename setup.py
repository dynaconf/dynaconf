
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='dynaconf',
    version="0.3.0",
    url='https://github.com/rochacbruno/dynaconf',
    license='MIT',
    author="Bruno Rocha",
    author_email="rochacbruno@gmail.com",
    description='Load Dynamic config',
    long_description="Load your configs in Dynamic way",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['six==1.10.0'],
    tests_require=[
        "pytest==2.8.3",
        "pytest-cov==2.2.0",
        "flake8==2.5.0",
        "pep8-naming==0.3.3",
        "flake8-debugger==1.4.0",
        "flake8-print==2.0.1",
        "flake8-todo==0.4",
        "radon==1.2.2"
    ],
    extras_require={
        "redis": ['redis==2.10.3'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ]
)
