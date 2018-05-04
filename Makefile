.PHONY: test install pep8 release clean doc

test_examples:
	@cd example/;python full_example.py
	@cd example/app;python app.py
	@cd example/app_with_dotenv;python app.py
	@cd example/multiple_sources;python app.py
	@cd example/toml_example/settings_module/;python app.py
	@cd example/yaml_example/settings_module/;python app.py
	@cd example/yaml_example/yaml_as_extra_config/;python app.py
	@cd example/flask_with_dotenv;flask routes
	@cd example/flask_with_toml;flask routes
	@cd example/flask_with_yaml;flask routes
	# @cd example/validator/;python app.py

test: pep8
	py.test -v --cov-config .coveragerc --cov=dynaconf -l --tb=short --maxfail=1 tests/

install:
	python setup.py develop

pep8:
	@flake8 dynaconf --ignore=F403

release: clean test
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
	python setup.py develop

doc:
	@epydoc --html dynaconf -o docs
