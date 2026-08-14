.PHONY: test

test:
	uv pip install pytest-django
	DJANGO_SETTINGS_MODULE=project.settings DJANGO_ENVIRONMENT=default pytest
	uv pip uninstall pytest-django
