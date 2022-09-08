.PHONY: test

test:
	rm -rf /tmp/dynaconf_project_root_test/settings.py
	mkdir -p /tmp/dynaconf_project_root_test/
	echo "MESSAGE = 'Hello from tmp'" > /tmp/dynaconf_project_root_test/settings.py
	python app.py
	rm -rf /tmp/dynaconf_project_root_test/
