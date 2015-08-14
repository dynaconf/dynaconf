.PHONY: test
test: pep8
	py.test /tests

.PHONY: pep8
pep8:
	@flake8 . --ignore=F403,E501

.PHONY: sdist
sdist:
	@python setup.py sdist upload

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
