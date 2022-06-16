# https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = get_wsgi_application()
