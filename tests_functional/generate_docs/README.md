# Generate Documentation Test

This functional test demonstrates the `dynaconf generate` command functionality.

## Files

- `settings.py` - Example settings file with type annotations
- `config.py` - Dynaconf configuration
- `Makefile` - Test commands

## Usage

Run the tests:
```bash
make test-all
```

Or run individual tests:
```bash
make test-json      # Test JSON output
make test-python    # Test Python output  
make test-markdown  # Test Markdown output
make test-toml      # Test TOML output
```

## Example Commands

Generate JSON schema:
```bash
cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f json
```

Generate Python documentation:
```bash
cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f python
```

Save to file:
```bash
cd ../.. && python -m dynaconf -i tests_functional/generate_docs/config.settings generate -f json -o schema.json
```