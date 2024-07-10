.PHONY: test

test:
	python manage.py test polls -v 2
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2
	cd ../../../;python tests_functional/legacy/django_example/manage.py test polls -v 2
	cd ../../../;PYTHONPATH=tests_functional/legacy/django_example/ DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings python standalone_script.py
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings dynaconf list
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings dynaconf get DEBUG
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings dynaconf inspect
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings dynaconf inspect -k BEST_BOSS
