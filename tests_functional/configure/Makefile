.PHONY: test

test:
	rm -rf /tmp/configure_test/settings.py
	mkdir -p /tmp/configure_test/
	echo "MESSAGE = 'Hello from tmp'" > /tmp/configure_test/settings.py
	python app.py
	rm -rf /tmp/configure_test/
