from __future__ import annotations

import copy
import os
import sys

import pytest

from dynaconf.base import LazySettings


@pytest.fixture(scope="module")
def settings():
    """Settings fixture with some defaults"""
    mode = "TRAVIS" if os.environ.get("TRAVIS") else "TEST"
    loaders = ["dynaconf.loaders.env_loader"]
    os.environ[f"DYNA{mode}_HOSTNAME"] = "host.com"
    os.environ[f"DYNA{mode}_PORT"] = "@int 5000"
    os.environ[f"DYNA{mode}_VALUE"] = "@float 42.1"
    os.environ[f"DYNA{mode}_ALIST"] = '@json ["item1", "item2", "item3"]'
    os.environ[f"DYNA{mode}_ADICT"] = '@json {"key": "value"}'
    os.environ[f"DYNA{mode}_DEBUG"] = "@bool true"
    os.environ[f"DYNA{mode}_TODELETE"] = "@bool true"
    sets = LazySettings(
        LOADERS_FOR_DYNACONF=loaders,
        ENVVAR_PREFIX_FOR_DYNACONF=f"DYNA{mode}",
        ROOT_PATH_FOR_DYNACONF=os.path.dirname(os.path.abspath(__file__)),
        environments=True,
        boxed_data={
            "HOST": "server.com",
            "port": 8080,
            "PARAMS": {
                "username": "admin",
                "PASSWORD": "secret",
                "token": {"TYPE": 1, "value": 2},
            },
        },
    )
    sets.SIMPLE_BOOL = False
    sets.configure()
    return sets


@pytest.fixture(scope="module")
def testdir():
    return os.path.dirname(os.path.abspath(__file__))


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    tmpdir.join(".env").write("DYNACONF_TESTING=true\n")

    # ensure local test created packages can be imported
    sys_path_bak = copy.deepcopy(sys.path)
    sys.path.insert(0, str(tmpdir))

    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield
    sys.path = sys_path_bak.copy()


@pytest.fixture(scope="module")
def clean_env(request):
    backup = copy.deepcopy(os.environ)
    for key in os.environ.keys():
        if key.startswith(("DYNACONF_", "FLASK_", "DJANGO_")):
            del os.environ[key]
    yield
    os.environ.update(backup)


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    """Get the docker-compose.yml absolute path.
    Override this fixture in your tests if you need a custom location.
    """
    return [os.path.join(os.getcwd(), "tests", "docker-compose.yml")]


@pytest.fixture(scope="session")
def docker_services_project_name():
    return "tests"
