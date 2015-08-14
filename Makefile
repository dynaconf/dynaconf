.PHONY: test
test: pep8
	py.test /tests

.PHONY: pep8
pep8:
	@flake8 . --ignore=F403

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
