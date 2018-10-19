.PHONY: test install pep8 release clean docs test_examples test_vault test_redis

test_examples:
	@cd example/common;pwd;python program.py
	@cd example/common-encoding;pwd;python program.py
	@cd example/;pwd;python full_example.py | grep -c full_example
	@cd example/;pwd;python compat.py
	@cd example/app;pwd;python app.py | grep -c app
	@cd example/app_with_dotenv;pwd;python app.py | grep -c app_with_dotenv
	@cd example/merge_configs;pwd;python app.py | grep -c merge_configs
	@cd example/multiple_sources;pwd;python app.py | grep -c multiple_sources
	@cd example/toml_example/;pwd;python app.py | grep -c toml_example
	@cd example/yaml_example/settings_module/;pwd;python app.py | grep -c yaml_example
	@cd example/yaml_example/yaml_as_extra_config/;pwd;python app.py | grep -c yaml_as_extra_config
	@cd example/flask_with_dotenv;pwd;flask routes | grep -c flask_with_dotenv
	@cd example/flask_with_toml;pwd;flask routes | grep -c flask_with_toml
	@cd example/flask_with_yaml;pwd;flask routes | grep -c flask_with_yaml
	@cd example/flask_with_json;pwd;flask routes | grep -c flask_with_json
	@cd example/flask_with_ini;pwd;flask routes | grep -c flask_with_ini
	@cd example/validators/with_python/;pwd;python app.py | grep -c validator
	@cd example/toml_with_secrets/;pwd;python program.py | grep -c My5up3r53c4et
	@cd example/envs;pwd;python app.py
	@cd example/django_example/;pwd;python manage.py test

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

test: pep8
	py.test --boxed -v --cov-config .coveragerc --cov=dynaconf -l --tb=short --maxfail=1 tests/

install:
	python setup.py develop

pep8:
	@flake8 dynaconf --ignore=F403

release: clean test_examples test
	@python setup.py sdist bdist_wheel
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
	python setup.py develop

docs:
	rm -rf docs/_build
	@cd docs;make html
