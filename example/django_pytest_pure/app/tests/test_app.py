import django

django.setup()  # noqa

import pytest

from django.contrib.auth import get_user_model
from django.conf import settings


@pytest.mark.django_db
def test_admin_user():
    User = get_user_model()

    assert User.objects.filter(username="admin").exists()
    assert settings.FOO == "bar"
