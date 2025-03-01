.PHONY: test

test:
	PYTHONPATH=. python src/app.py
	dynaconf -i src.app.settings inspect -m debug -vv