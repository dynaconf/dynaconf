from __future__ import annotations

import pytest
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    # https://github.com/dynaconf/dynaconf/issues/491#issuecomment-745391955
    from django.conf import settings

    settings.setenv("pytest")


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "project/fixtures/admin.json")
