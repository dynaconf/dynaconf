.PHONY: test clean

export FLASK_APP=app:create_app

test: clean
	dynaconf init -v test_var
	grep '\[development\]' settings.toml

clean:
	rm -rf settings.toml
	rm -rf .secrets.toml
	rm -rf .gitignore
