"""Documentation generation utilities for Dynaconf settings."""

from __future__ import annotations

import ast
import inspect
import json
import types
from pathlib import Path
from typing import Any
from typing import Dict
from typing import get_type_hints
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from dynaconf.loaders.py_loader import get_module
from dynaconf.utils import DynaconfDict
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.vendor import toml


def extract_annotations_from_python_file(file_path: str) -> Dict[str, Any]:
    """Extract type annotations from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        annotations = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(
                node.target, ast.Name
            ):
                var_name = node.target.id
                if node.annotation:
                    annotations[var_name] = ast.get_source_segment(
                        content, node.annotation
                    )

        return annotations
    except Exception:
        return {}


def extract_annotations_from_module(
    module: types.ModuleType,
) -> Dict[str, Any]:
    """Extract type annotations from a module object."""
    try:
        return get_type_hints(module)
    except Exception:
        return {}


def extract_docstring_from_annotated(annotation_str: str) -> Optional[str]:
    """Extract documentation from Annotated type hints."""
    if "Annotated" not in annotation_str:
        return None

    try:
        # Simple regex-based extraction for Doc() strings
        import re

        doc_match = re.search(r'Doc\(["\']([^"\']*)["\']', annotation_str)
        if doc_match:
            return doc_match.group(1)
    except Exception:
        pass

    return None


def get_base_type_name(type_hint: Any) -> str:
    """Get the base type name from a type hint."""
    if hasattr(type_hint, "__origin__"):
        # Handle generic types like List[str], Dict[str, int], etc.
        origin = type_hint.__origin__
        if origin is Union:
            # Handle Union types (Optional is Union[X, None])
            args = getattr(type_hint, "__args__", ())
            if len(args) == 2 and type(None) in args:
                # This is Optional[X]
                non_none_type = next(
                    arg for arg in args if arg is not type(None)
                )
                return f"Optional[{get_base_type_name(non_none_type)}]"
            else:
                # This is Union[X, Y, ...]
                arg_names = [get_base_type_name(arg) for arg in args]
                return f"Union[{', '.join(arg_names)}]"
        else:
            # Handle other generic types
            return getattr(origin, "__name__", str(origin))
    elif hasattr(type_hint, "__name__"):
        return type_hint.__name__
    else:
        return str(type_hint)


def extract_settings_schema(
    obj, settings_files: List[str]
) -> Dict[str, Dict[str, Any]]:
    """Extract schema information from settings files."""
    schema = {}

    for settings_file in settings_files:
        if settings_file.endswith(".py"):
            # Handle Python settings files
            try:
                mod, loaded_from = get_module(obj, settings_file, silent=True)
                if mod and loaded_from:
                    # Extract annotations from the module
                    annotations = extract_annotations_from_module(mod)
                    # Use the actual file path from settings_file, not the returned loaded_from
                    file_annotations = extract_annotations_from_python_file(
                        settings_file
                    )

                    # Get all module attributes, excluding imports and internal types
                    excluded_types = {
                        "module",
                        "type",
                        "function",
                        "_Feature",
                        "_SpecialForm",
                        "_SpecialGenericAlias",
                        "_TypedCacheSpecialForm",
                        "_GenericAlias",
                    }
                    excluded_names = {
                        "annotations",
                        "Dict",
                        "List",
                        "Optional",
                        "Annotated",
                        "Doc",
                    }

                    module_vars = {}
                    for name in dir(mod):
                        if (
                            not name.startswith("_")
                            and name not in excluded_names
                            and name.isupper()
                        ):  # Only include UPPER_CASE settings
                            value = getattr(mod, name)
                            value_type = type(value).__name__
                            if value_type not in excluded_types:
                                module_vars[name] = value

                    for var_name, value in module_vars.items():
                        # Extract documentation from Annotated types in file annotations
                        doc = None
                        if var_name in file_annotations:
                            doc = extract_docstring_from_annotated(
                                file_annotations[var_name]
                            )

                        if var_name in annotations:
                            type_hint = annotations[var_name]
                            type_name = get_base_type_name(type_hint)

                            schema[var_name] = {
                                "type": type_name,
                                "default": value,
                                "source": settings_file,
                                "doc": doc,
                            }
                        else:
                            # No type annotation, infer from value
                            schema[var_name] = {
                                "type": type(value).__name__,
                                "default": value,
                                "source": settings_file,
                                "doc": doc,
                            }
            except Exception:
                # If we can't load the Python file, skip it
                continue

    return schema


def generate_python_docs(schema: Dict[str, Dict[str, Any]]) -> str:
    """Generate Python documentation from schema."""
    lines = [
        '"""',
        "Settings Schema Documentation",
        "=" * 32,
        "",
        "This file contains the schema for all settings in this project.",
        '"""',
        "",
        "from typing import *",
        "from typing_extensions import Annotated",
        "",
        "# Type alias for documentation",
        "Doc = lambda x: x",
        "",
    ]

    for var_name, info in sorted(schema.items()):
        type_name = info["type"]
        default = info["default"]
        doc = info["doc"]
        source = info["source"]

        # Add comment with source information
        lines.append(f"# Source: {source}")

        # Format the variable declaration
        if doc:
            lines.append(
                f'{var_name}: Annotated[{type_name}, Doc("{doc}")] = {repr(default)}'
            )
        else:
            lines.append(f"{var_name}: {type_name} = {repr(default)}")

        lines.append("")

    return "\n".join(lines)


def generate_json_docs(schema: Dict[str, Dict[str, Any]]) -> str:
    """Generate JSON documentation from schema."""
    json_schema = {
        "title": "Settings Schema",
        "description": "Schema for all settings in this project",
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }

    for var_name, info in schema.items():
        type_name = info["type"]
        default = info["default"]
        doc = info["doc"]
        source = info["source"]

        # Map Python types to JSON Schema types
        json_type = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "NoneType": "null",
        }.get(type_name.lower(), "string")

        property_def = {
            "type": json_type,
            "default": default,
            "source": source,
        }

        if doc:
            property_def["description"] = doc

        json_schema["properties"][var_name] = property_def

    return json.dumps(json_schema, indent=2)


def generate_toml_docs(schema: Dict[str, Dict[str, Any]]) -> str:
    """Generate TOML documentation from schema."""
    lines = [
        "# Settings Schema Documentation",
        "# ==============================",
        "#",
        "# This file contains the schema for all settings in this project.",
        "#",
        "",
        "[schema]",
        "",
    ]

    for var_name, info in sorted(schema.items()):
        type_name = info["type"]
        default = info["default"]
        doc = info["doc"]
        source = info["source"]

        # Add documentation comments
        lines.append(f"# {var_name}")
        lines.append(f"#   Type: {type_name}")
        lines.append(f"#   Source: {source}")
        if doc:
            lines.append(f"#   Description: {doc}")

        # Add the actual setting with its default value
        try:
            if isinstance(default, str):
                lines.append(f'{var_name} = "{default}"')
            elif isinstance(default, (int, float, bool)):
                lines.append(f"{var_name} = {default}")
            elif isinstance(default, (list, dict)):
                # For complex types, use TOML representation
                lines.append(f"# {var_name} = {repr(default)}  # Complex type")
            else:
                lines.append(f"# {var_name} = {repr(default)}  # {type_name}")
        except Exception:
            lines.append(f"# {var_name} = {repr(default)}  # {type_name}")

        lines.append("")

    return "\n".join(lines)


def generate_markdown_docs(schema: Dict[str, Dict[str, Any]]) -> str:
    """Generate Markdown documentation from schema."""
    lines = [
        "# Settings Schema Documentation",
        "",
        "This document describes all the settings available in this project.",
        "",
        "## Settings",
        "",
    ]

    for var_name, info in sorted(schema.items()):
        type_name = info["type"]
        default = info["default"]
        doc = info["doc"]
        source = info["source"]

        lines.append(f"### `{var_name}`")
        lines.append("")
        lines.append(f"- **Type:** `{type_name}`")
        lines.append(f"- **Default:** `{repr(default)}`")
        lines.append(f"- **Source:** `{source}`")

        if doc:
            lines.append(f"- **Description:** {doc}")

        lines.append("")

    return "\n".join(lines)


def generate_yaml_docs(schema: Dict[str, Dict[str, Any]]) -> str:
    """Generate YAML documentation from schema."""
    try:
        import yaml

        yaml_schema = {
            "title": "Settings Schema",
            "description": "Schema for all settings in this project",
            "properties": {},
        }

        for var_name, info in schema.items():
            yaml_schema["properties"][var_name] = {
                "type": info["type"],
                "default": info["default"],
                "source": info["source"],
            }

            if info["doc"]:
                yaml_schema["properties"][var_name]["description"] = info[
                    "doc"
                ]

        return yaml.dump(yaml_schema, default_flow_style=False, indent=2)
    except ImportError:
        # If PyYAML is not available, generate a simple YAML-like format
        lines = [
            "title: Settings Schema",
            "description: Schema for all settings in this project",
            "properties:",
        ]

        for var_name, info in sorted(schema.items()):
            lines.append(f"  {var_name}:")
            lines.append(f'    type: {info["type"]}')
            lines.append(f'    default: {repr(info["default"])}')
            lines.append(f'    source: {info["source"]}')
            if info["doc"]:
                lines.append(f'    description: {info["doc"]}')

        return "\n".join(lines)


def generate_docs(obj, output_format: str = "json") -> str:
    """Generate documentation for settings based on their schema."""
    # Force loading of settings if not already loaded
    if not hasattr(obj, "_loaded_files") or not obj._loaded_files:
        # Trigger loading by accessing a dummy key
        try:
            _ = obj.get("_DUMMY_KEY_TO_TRIGGER_LOADING", None)
        except:
            pass

    # Get settings files from the object
    settings_files = getattr(obj, "_loaded_files", [])
    if not settings_files:
        settings_files = getattr(obj, "_settings_files", [])
    if not settings_files:
        settings_files = getattr(obj, "settings_files", [])

    # Extract schema from settings files
    schema = extract_settings_schema(obj, settings_files)

    # Generate documentation in the requested format
    if output_format == "python":
        return generate_python_docs(schema)
    elif output_format == "json":
        return generate_json_docs(schema)
    elif output_format == "toml":
        return generate_toml_docs(schema)
    elif output_format == "markdown":
        return generate_markdown_docs(schema)
    elif output_format == "yaml":
        return generate_yaml_docs(schema)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
