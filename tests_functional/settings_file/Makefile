.PHONY: test

test:
	rm -rf /tmp/settings_file_test/settings.py
	mkdir -p /tmp/settings_file_test/
	echo "MESSAGE = 'Hello from tmp'" > /tmp/settings_file_test/settings.py
	python app.py
	rm -rf /tmp/settings_file_test/
