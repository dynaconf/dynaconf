.PHONY: test

test:
	python manage.py test polls -v 2
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2
	cd ../../../;python tests_functional/legacy/django_example_compat/manage.py test polls -v 2
	cd ../../../;PYTHONPATH=tests_functional/legacy/django_example_compat/ DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings python standalone_script.py
