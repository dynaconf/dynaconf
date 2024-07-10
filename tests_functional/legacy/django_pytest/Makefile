.PHONY: test

test:
	pip install pytest-django
	DJANGO_SETTINGS_MODULE=project.settings DJANGO_ENVIRONMENT=default pytest
	pip uninstall -y pytest-django
