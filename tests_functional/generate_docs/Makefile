#!/usr/bin/make -f

# Test the generate command functionality

.PHONY: test-json test-python test-markdown test-toml test-all clean

test-json:
	@echo "Testing JSON output..."
	@cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f json

test-python:
	@echo "Testing Python output..."
	@cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f python

test-markdown:
	@echo "Testing Markdown output..."
	@cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f markdown

test-toml:
	@echo "Testing TOML output..."
	@cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f toml

test-output-file:
	@echo "Testing output to file..."
	@cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f json -o /tmp/schema.json
	@echo "Generated schema saved to /tmp/schema.json"
	@cat /tmp/schema.json

test-all: test-json test-python test-markdown test-toml test-output-file

clean:
	@rm -f /tmp/schema.json