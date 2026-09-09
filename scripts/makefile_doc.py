#!/usr/bin/env python3
"""Print `target  description` help lines from a Makefile, grouped by section header.

A target is documented by a `#:` comment line immediately above it, e.g.:

    #: Install WHEEL and/or GROUP (uv dependency group) into ./.venv
    install:
        ...

A `|` in the docstring separates the description (left) from a note about
optional args (right), which is printed dimmed, e.g.:

    #: Install into ./.venv | WHEEL=dist/*.whl GROUP=test PYTHON=3.11
    install:
        ...

Set NO_COLOR (https://no-color.org/) to any non-empty value to disable colors.
"""
# ruff: noqa: T201  # this CLI script's whole purpose is printing to stdout

import os
import re
import sys

RULE_RE = re.compile(r"^#\s*-{10,}\s*$")
SECTION_RE = re.compile(r"^#\s*(.+?)\s*$")
DOC_RE = re.compile(r"^#:\s*(.*)$")
TARGET_RE = re.compile(r"^([a-zA-Z_-]+):")

NO_COLOR = bool(os.environ.get("NO_COLOR"))
CYAN = "" if NO_COLOR else "\033[36m"
BOLD = "" if NO_COLOR else "\033[1m"
DIM = "" if NO_COLOR else "\033[2;90m"
RESET = "" if NO_COLOR else "\033[0m"


def parse(lines):
    sections = {}
    section = "Other"
    prev_was_rule = False
    pending_doc = None
    for line in lines:
        if RULE_RE.match(line):
            prev_was_rule = True
            continue
        if prev_was_rule:
            match = SECTION_RE.match(line)
            if match:
                section = match.group(1)
            prev_was_rule = False
            continue

        doc_match = DOC_RE.match(line)
        if doc_match:
            pending_doc = doc_match.group(1)
            continue

        target_match = TARGET_RE.match(line)
        if target_match and pending_doc is not None:
            sections.setdefault(section, {})[target_match.group(1)] = (
                pending_doc
            )

        pending_doc = None
    return sections


def main():
    sections = parse(sys.stdin)
    width = (
        max(len(name) for targets in sections.values() for name in targets) + 2
    )
    for section, targets in sections.items():
        if not targets:
            continue
        print(f"{BOLD}{section}{RESET}")
        for name in sorted(targets):
            padded_name = f"{name:<{width}}"
            desc, sep, note = targets[name].partition("|")
            desc = desc.strip()
            note = f" {DIM}{sep} {note.strip()}{RESET}" if note else ""
            print(f"    {CYAN}{padded_name}{RESET}{desc}{note}")


if __name__ == "__main__":
    main()
