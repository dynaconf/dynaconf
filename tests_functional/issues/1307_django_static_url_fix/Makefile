.PHONY: test

test:
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=project.settings django-admin shell -c "from django.conf import settings;settings.STATIC_URL == '/static/' or exit(1)"
