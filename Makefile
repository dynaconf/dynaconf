.PHONY: test install pep8 release clean doc

test: pep8
	py.test -v --cov=dynaconf -l --tb=short --maxfail=1 tests/

install:
	python setup.py develop

pep8:
	@flake8 dynaconf --ignore=F403

release: test
	@python setup.py sdist bdist_wheel upload

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
