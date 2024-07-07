from __future__ import annotations

import django

django.setup()  # noqa

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings


@pytest.mark.django_db
def test_admin_user():
    User = get_user_model()

    assert User.objects.filter(username="admin").exists()
    assert settings.FOO == "foo-test"


@override_settings(CONTENT_APP_TTL=30)
def test_settings_override_689():
    # before
    assert settings.CONTENT_APP_TTL == 30

    # after
    with override_settings(CONTENT_APP_TTL=1):
        assert settings.CONTENT_APP_TTL == 1

    # same as before
    assert settings.CONTENT_APP_TTL == 30
