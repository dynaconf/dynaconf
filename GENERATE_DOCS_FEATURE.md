# Generate Documentation Feature

This document describes the new `dynaconf generate` command that generates documentation from settings schema based on type annotations.

## Overview

The `dynaconf generate` command extracts type annotations from Python settings files and generates documentation in various formats. It supports:

- **Type Annotations**: `foo: int = 42`
- **Documented Types**: `foo: Annotated[int, Doc("This is an integer")] = 42`
- **Multiple Output Formats**: Python, JSON, TOML, Markdown, YAML

## Usage

### Basic Usage

```bash
# Generate JSON schema documentation
dynaconf -i config.settings generate -f json

# Generate Python documentation
dynaconf -i config.settings generate -f python

# Generate Markdown documentation
dynaconf -i config.settings generate -f markdown
```

### Save to File

```bash
# Save JSON schema to file
dynaconf -i config.settings generate -f json -o schema.json

# Save Python documentation to file
dynaconf -i config.settings generate -f python -o schema.py

# Save Markdown documentation to file
dynaconf -i config.settings generate -f markdown -o SETTINGS.md
```

## Supported Input Formats

### Python Settings Files

The command analyzes Python settings files that contain type annotations:

```python
# settings.py
from typing import Dict, List, Optional
from typing_extensions import Annotated

# Type alias for documentation
Doc = lambda x: x

# Basic type annotations
DEBUG: bool = False
PORT: int = 8000
HOST: str = "localhost"

# Documented annotations
DATABASE_URL: Annotated[str, Doc("Connection string for the database")] = "sqlite:///app.db"
CACHE_TIMEOUT: Annotated[int, Doc("Cache timeout in seconds")] = 300

# Complex types
ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
DATABASE_CONFIG: Dict[str, str] = {"ENGINE": "postgresql", "NAME": "mydb"}

# Optional types
SECRET_KEY: Optional[str] = None
REDIS_URL: Annotated[Optional[str], Doc("Redis connection URL")] = None
```

## Output Formats

### JSON Schema

Generates a JSON Schema document:

```json
{
  "title": "Settings Schema",
  "description": "Schema for all settings in this project",
  "type": "object",
  "properties": {
    "DEBUG": {
      "type": "boolean",
      "default": false,
      "source": "settings.py"
    },
    "DATABASE_URL": {
      "type": "string",
      "default": "sqlite:///app.db",
      "source": "settings.py",
      "description": "Connection string for the database"
    }
  }
}
```

### Python Documentation

Generates a Python file with type annotations:

```python
"""
Settings Schema Documentation
================================

This file contains the schema for all settings in this project.
"""

from typing import *
from typing_extensions import Annotated

# Type alias for documentation
Doc = lambda x: x

# Source: settings.py
DEBUG: bool = False

# Source: settings.py
DATABASE_URL: Annotated[str, Doc("Connection string for the database")] = "sqlite:///app.db"
```

### Markdown Documentation

Generates human-readable Markdown documentation:

```markdown
# Settings Schema Documentation

This document describes all the settings available in this project.

## Settings

### `DEBUG`

- **Type:** `bool`
- **Default:** `False`
- **Source:** `settings.py`

### `DATABASE_URL`

- **Type:** `str`
- **Default:** `"sqlite:///app.db"`
- **Source:** `settings.py`
- **Description:** Connection string for the database
```

### TOML Documentation

Generates TOML format documentation:

```toml
# Settings Schema Documentation
# ==============================

[schema]

# DEBUG
#   Type: bool
#   Source: settings.py
DEBUG = false

# DATABASE_URL
#   Type: str
#   Source: settings.py
#   Description: Connection string for the database
DATABASE_URL = "sqlite:///app.db"
```

### YAML Documentation

Generates YAML format documentation:

```yaml
title: Settings Schema
description: Schema for all settings in this project
properties:
  DEBUG:
    type: bool
    default: false
    source: settings.py
  DATABASE_URL:
    type: str
    default: sqlite:///app.db
    source: settings.py
    description: Connection string for the database
```

## Implementation Details

### Core Components

1. **dynaconf/utils/docgen.py** - Main documentation generation logic
2. **dynaconf/cli.py** - CLI command implementation  
3. **tests/test_generate.py** - Unit tests
4. **tests_functional/generate_docs/** - Functional tests

### Key Features

- **Type Annotation Extraction**: Parses Python AST to extract type hints
- **Documentation Extraction**: Extracts `Doc()` strings from `Annotated` types
- **Multiple Output Formats**: Supports JSON, Python, Markdown, TOML, YAML
- **Settings File Discovery**: Automatically finds and processes loaded settings files
- **Error Handling**: Graceful handling of missing files or malformed annotations

### Dependencies

- Uses existing dynaconf infrastructure
- Leverages Python's `typing` and `ast` modules
- No additional external dependencies required

## Testing

Run the tests with:

```bash
# Run unit tests
python -m pytest tests/test_generate.py -v

# Run functional tests
cd tests_functional/generate_docs
make test-all
```

## Examples

See `tests_functional/generate_docs/` for a complete working example with:
- Sample settings file with type annotations
- Configuration setup
- Test commands for all output formats

## Error Handling

The command handles various error conditions gracefully:

- Missing or malformed settings files
- Invalid type annotations
- Missing documentation strings
- Unsupported output formats
- File write permissions

## Future Enhancements

Possible future improvements:

1. Support for additional input formats (TOML, YAML settings files)
2. Enhanced documentation with examples and validation rules
3. Integration with schema validation libraries
4. Support for nested settings structures
5. Custom output templates
6. Integration with documentation generation tools