#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from time import sleep

from dynaconf.vendor.tomllib import load

HERE = Path(__file__).parent
skips = load(open(HERE / "skipfile.toml", "rb")).get(os.name, [])

print("Starting Functional Tests")
print("-" * 40)


def execute_test(filename, cmd, path, env):
    if (path / filename).exists():
        print(f"Running {filename}")
        subprocess.check_call(cmd, cwd=path, env=env)

        # try to also execute from parent folder
        if filename not in ["Makefile", "test.sh"]:
            print("Running from parent folder")
            subprocess.check_call(
                [sys.executable, path.resolve() / filename],
                cwd=path.parent,
                env=env,
            )

        return True  # test executed with success
    return False  # test not executed because file not found


def execute_tests(path):
    print("-" * 40)
    print("Starting Test on:", path)

    if path.name in skips:
        print(f"Skipping {path} on {os.name}")
        return True

    env = {**os.environ}
    if os.path.exists(path / "env.toml"):
        print("Loading env.toml")
        _envvars = load(open(path / "env.toml", "rb"))
        env.update(_envvars)

    # Order matters
    test_files = [
        ("Makefile", ["make", "test"]),
        ("test.sh", ["bash", "test.sh"]),
        ("test.py", [sys.executable, "test.py"]),
        ("app.py", [sys.executable, "app.py"]),
        ("program.py", [sys.executable, "program.py"]),
        ("manage.py", [sys.executable, "manage.py", "test"]),
    ]

    for filename, cmd in test_files:
        if execute_test(filename, cmd, path, env):
            return True
    return False


def run_tests(show_list=False, test_filter=None):
    def filter_allowed(testpath):
        if not test_filter:
            return True
        for keyword in test_filter:
            if keyword in testpath.name:
                return True
        return False

    passed = 0
    root_directory = Path(__file__).parent
    print("Workdir:", root_directory.absolute())
    functional_tests = sorted(list(root_directory.iterdir()))
    print("Collected functional tests:", len(functional_tests))
    sleep(1)

    for path in functional_tests:
        if path.is_dir():
            if path.name in [".", "__pycache__"]:
                continue

            if show_list:
                print(path)
            else:
                if filter_allowed(path) and execute_tests(path):
                    passed += 1
                    print(f"Passed {path}")
                    continue

            # Now Subdirectories one level
            subdirs = sorted(list(path.iterdir()))
            for subdir in subdirs:
                if subdir.is_dir():
                    if subdir.name in [".", "__pycache__"]:
                        continue

                    if show_list:
                        print(subdir)
                    else:
                        if filter_allowed(subdir) and execute_tests(subdir):
                            passed += 1
                            print(f"Passed {subdir}")
                            continue

            if not subdirs:
                exit(
                    "WARNING: Can't find a testable file, "
                    "Makefile, test.sh, app.py, test.py, program.py"
                )

    if not show_list:
        print("-" * 40)
        print(f"{passed} functional tests passed")
        print("-" * 40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list",
        dest="show_list",
        action="store_true",
        help="List all available tests (do not execute)",
    )
    parser.add_argument(
        "--filter",
        dest="test_filter",
        action="append",
        help="limt tests to those that contain a substring",
    )
    args = parser.parse_args()
    run_tests(show_list=args.show_list, test_filter=args.test_filter)
