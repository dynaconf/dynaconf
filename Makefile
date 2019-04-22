SHELL := /bin/bash
.PHONY: all clean dist docs install pep8 publish run-pre-commit run-tox setup-pre-commit test test_examples test_only test_redis test_vault help coverage-report

help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

all: clean install run-pre-commit test test_examples coverage-report

test_examples:
	@echo '###############  Chdir to example directory  ###############'
	cd example/common;pwd;python program.py
	cd example/common-encoding;pwd;python program.py
	cd example/;pwd;python full_example.py | grep -c full_example || exit 1
	cd example/;pwd;python compat.py
	cd example/app;pwd;python app.py | grep -c app || exit 1
	cd example/app_with_dotenv;pwd;python app.py | grep -c app_with_dotenv || exit 1
	cd example/merge_configs;pwd;python app.py | grep -c merge_configs || exit 1
	cd example/dynaconf_merge;pwd;python app.py
	cd example/multiple_sources;pwd;python app.py | grep -c multiple_sources || exit 1
	cd example/multiple_folders;pwd;python app.py | grep -c var2_prod || exit 1
	cd example/toml_example/;pwd;python app.py | grep -c toml_example || exit 1
	cd example/yaml_example/settings_file/;pwd;python app.py | grep -c yaml_example || exit 1
	cd example/yaml_example/yaml_as_extra_config/;pwd;python app.py | grep -c yaml_as_extra_config || exit 1
	cd example/flask_with_dotenv;pwd;flask routes | grep -c flask_with_dotenv || exit 1
	cd example/flask_with_toml;pwd;flask routes | grep -c flask_with_toml || exit 1
	cd example/flask_with_yaml;pwd;flask routes | grep -c flask_with_yaml || exit 1
	cd example/flask_with_json;pwd;flask routes | grep -c flask_with_json || exit 1
	cd example/flask_with_commentjson;pwd;flask routes | grep -c flask_with_commentjson || exit 1
	cd example/flask_with_ini;pwd;flask routes | grep -c flask_with_ini || exit 1
	cd example/validators/with_python/;pwd;python app.py | grep -c validator || exit 1
	cd example/validators/with_toml/;pwd;dynaconf validate
	cd example/toml_with_secrets/;pwd;python program.py | grep -c My5up3r53c4et || exit 1
	cd example/envs;pwd;python app.py
	cd example/custom_loader;pwd;python app.py
	cd example/get_fresh;pwd;python app.py
	cd example/includes;pwd;python app.py
	cd example/jenkins_secrets_file;pwd;python app.py
	cd example/specific_settings_files;pwd;python app.py
	cd example/django_example/;pwd;python manage.py test polls -v 2
	cd example/django_example_compat/;pwd;python manage.py test polls -v 2
	cd example/django_example/;pwd;PYTHONPATH=. DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2
	cd example/project_root/;pwd;rm -rf /tmp/dynaconf_project_root_test/settings.py;mkdir -p /tmp/dynaconf_project_root_test/;echo "MESSAGE = 'Hello from tmp'" > /tmp/dynaconf_project_root_test/settings.py;python app.py;rm -rf /tmp/dynaconf_project_root_test/
	cd example/settings_file/;pwd;rm -rf /tmp/settings_file_test/settings.py;mkdir -p /tmp/settings_file_test/;echo "MESSAGE = 'Hello from tmp'" > /tmp/settings_file_test/settings.py;python app.py;rm -rf /tmp/settings_file_test/
	cd example/configure/;pwd;rm -rf /tmp/configure_test/settings.py;mkdir -p /tmp/configure_test/;echo "MESSAGE = 'Hello from tmp'" > /tmp/configure_test/settings.py;python app.py;rm -rf /tmp/configure_test/

	@echo '###############  Calling from outer folder  ###############'
	python example/common/program.py
	python example/common-encoding/program.py
	python example/full_example.py | grep -c full_example || exit 1
	python example/compat.py
	python example/app/app.py | grep -c app || exit 1
	python example/app_with_dotenv/app.py | grep -c app_with_dotenv || exit 1
	python example/merge_configs/app.py | grep -c merge_configs || exit 1
	python example/dynaconf_merge/app.py
	python example/multiple_sources/app.py | grep -c multiple_sources || exit 1
	python example/multiple_folders/app.py | grep -c var2_prod || exit 1
	python example/toml_example/app.py | grep -c toml_example || exit 1
	python example/yaml_example/settings_file/app.py | grep -c yaml_example || exit 1
	python example/yaml_example/yaml_as_extra_config/app.py | grep -c yaml_as_extra_config || exit 1
	python example/validators/with_python/app.py | grep -c validator || exit 1
	python example/toml_with_secrets/program.py | grep -c My5up3r53c4et || exit 1
	python example/envs/app.py
	python example/custom_loader/app.py
	python example/get_fresh/app.py
	python example/includes/app.py
	python example/jenkins_secrets_file/app.py
	python example/specific_settings_files/app.py
	python example/django_example/manage.py test polls -v 2
	PYTHONPATH=example/django_example DJANGO_SETTINGS_MODULE=foo.settings python example/django_example/standalone_script.py
	PYTHONPATH=example/django_example_compat DJANGO_SETTINGS_MODULE=foo.settings python example/django_example_compat/standalone_script.py
	python example/envvar_prefix/app.py

	@echo '###############  Django Admin From root folder  ###############'
	PYTHONPATH=./example/django_example/ DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2
	PYTHONPATH=./example/django_example_compat/ DJANGO_SETTINGS_MODULE=foo.settings django-admin test polls -v 2

	@echo '############ Issues  ##################'
	cd example/issues/160_path_traversal_fixed;pwd;./test.sh
	cd example/issues/166_renamed_global_env;pwd;python app.py
	cd example/issues/169_renamed_settings_module;pwd;python app.py

test_vault:
	# @cd example/vault;pwd;python write.py
	@cd example/vault;pwd;dynaconf write vault -s SECRET=vault_works
	@cd example/vault;pwd;dynaconf write vault -e dev -s SECRET=vault_works_in_dev
	@sleep 5
	@cd example/vault;pwd;python vault_example.py | grep -c vault_works

test_redis:
	# @cd example/redis_example;pwd;python write.py
	@cd example/redis_example;pwd;dynaconf write redis -s SECRET=redis_works
	@cd example/redis_example;pwd;dynaconf write redis -e dev -s SECRET=redis_works_in_dev
	@sleep 5
	@cd example/redis_example;pwd;python redis_example.py | grep -c redis_works

test_only:
	py.test --boxed -v --cov-config .coveragerc --cov=dynaconf -l --tb=short --maxfail=1 tests/
	coverage xml

coverage-report:
	coverage report --fail-under=100

test: pep8 test_only

install:
	pip install --upgrade pip
	python setup.py develop
	pip install -r requirements_dev.txt
	make setup-pre-commit

setup-pre-commit:
	pre-commit install
	pre-commit install-hooks

run-pre-commit:
	pre-commit run --files $$(find -regex '.*\.\(py\|yaml\|yml\|md\)') -v

pep8:
	# Flake8 ignores
	#   F841 (local variable assigned but never used, useful for debugging on exception)
	#   W504 (line break after binary operator, I prefer to put `and|or` at the end)
	#   F403 (star import `from foo import *` often used in __init__ files)
	flake8 dynaconf --ignore=F403,W504,W503,F841,E401,F401,E402

dist: clean
	@python setup.py sdist bdist_wheel

publish:
	make run-tox
	@twine upload dist/*

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build

docs:
	rm -rf docs/_build
	@cd docs;make html

run-tox:
	tox -r
	rm -rf .tox
