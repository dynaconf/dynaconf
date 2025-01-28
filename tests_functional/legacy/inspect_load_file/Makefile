.PHONY: test

test:
	# ensure inspect shows the loader when load_file is called
	dynaconf -i app.settings inspect -k FROM_TOML | grep '"loader": "load_file@'
	dynaconf -i app.settings inspect -k FROM_PYTHON | grep '"loader": "load_file@'
	dynaconf -i app.settings inspect -k FROM_YAML | grep '"loader": "yaml"'

