
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
    ).read()


def parse_md_to_rst(file):
    """Read Markdown file and convert to ReStructured Text.""" 
    try:
        from pypandoc import convert_file
        return convert_file(file, 'rst')
    except ImportError:
        # pypandoc may not be installed in user environment
        try:
            return read(file)
        except:
            return file.read()


setup(
    name='dynaconf',
    version="0.5.2",
    url='https://github.com/rochacbruno/dynaconf',
    license='MIT',
    author="Bruno Rocha",
    author_email="rochacbruno@gmail.com",
    description='The dynamic configurator for your Python Project',
    long_description=parse_md_to_rst("README.md"),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['six', 'python-box'],
    tests_require=[
        "pytest",
        "pytest-cov",
        "flake8",
        "pep8-naming",
        "flake8-debugger",
        "flake8-print",
        "flake8-todo",
        "radon",
        "flask>=0.12"
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
