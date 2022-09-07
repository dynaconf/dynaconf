.PHONY: test

export FLASK_APP=app:create_app

test:
	dynaconf init -v test_var || true
	# if settings.toml exists exit with error
	if [ -f settings.toml ]; then exit 1; fi
