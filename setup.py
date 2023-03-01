from __future__ import annotations

import os

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    """Read a file."""
    content = ""
    with open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


test_requirements = [
    "pytest",
    "pytest-cov",
    "pytest-xdist",
    "pytest-mock",
    "flake8",
    "pep8-naming",
    "flake8-debugger",
    "flake8-print",
    "flake8-todo",
    "radon",
    "flask>=0.12",
    "django",
    "python-dotenv",
    "toml",
    "codecov",
    "redis",
    "hvac",
    "configobj",
]


setup(
    name="dynaconf",
    version=read("dynaconf", "VERSION"),
    url="https://github.com/dynaconf/dynaconf",
    license="MIT",
    license_files=["LICENSE", "vendor_licenses/*"],
    author="Bruno Rocha",
    author_email="rochacbruno@gmail.com",
    description="The dynamic configurator for your Python Project",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "tests_functional",
            "tests_functional.*",
            "docs",
            "legacy_docs",
            "legacy_docs.*",
            "docs.*",
            "build",
            "build.*",
            "dynaconf.vendor_src",
            "dynaconf/vendor_src",
            "dynaconf.vendor_src.*",
            "dynaconf/vendor_src/*",
        ]
    ),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    tests_require=test_requirements,
    extras_require={
        "redis": ["redis"],
        "vault": ["hvac"],
        "yaml": ["ruamel.yaml"],
        "toml": ["toml"],
        "ini": ["configobj"],
        "configobj": ["configobj"],
        "all": ["redis", "ruamel.yaml", "configobj", "hvac"],
        "test": test_requirements,
    },
    python_requires=">=3.8",
    entry_points={"console_scripts": ["dynaconf=dynaconf.cli:main"]},
    setup_requires=["setuptools>=38.6.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
