.PHONY: test

test:
	# ensure inspect shows the loader when load_file is called
	dynaconf -i app.settings inspect -k FROM_TOML | grep '"loader": "load_file@'
	dynaconf -i app.settings inspect -k FROM_PYTHON | grep '"loader": "load_file@'
	dynaconf -i app.settings inspect -k FROM_YAML | grep '"loader": "yaml"'
	dynaconf -i app.settings inspect -k '_(TOML|PYTHON)$$' --regex | python -c "import json, sys; r = json.load(sys.stdin); assert r['current'] == {'FROM_TOML': 'thefile.toml', 'FROM_PYTHON': 'thefile.py'}"

