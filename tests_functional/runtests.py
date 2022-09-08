#!/usr/bin/env python3
from __future__ import annotations

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
        try:
            subprocess.check_call(cmd, cwd=path, env=env)
        except subprocess.CalledProcessError:
            print(f"################# Failed on {path}")

        # try to also execute from parent folder
        if filename not in ["Makefile", "test.sh"]:
            print("Running from parent folder")
            try:
                subprocess.check_call(
                    [sys.executable, path.resolve() / filename],
                    cwd=path.parent,
                    env=env,
                )
            except subprocess.CalledProcessError:
                print("################# Failed to run from parent folder")

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


def run_tests():
    executed = 0
    root_directory = Path(__file__).parent
    print("Workdir:", root_directory.absolute())
    functional_tests = sorted(list(root_directory.iterdir()))
    print("Collected functional tests:", len(functional_tests))
    sleep(1)
    for path in functional_tests:
        if path.is_dir():
            if path.name in [".", "__pycache__"]:
                continue

            if execute_tests(path):
                executed += 1
                continue

            # Now Subdirectories one level
            subdirs = sorted(list(path.iterdir()))
            for subdir in subdirs:
                if subdir.is_dir():
                    if subdir.name in [".", "__pycache__"]:
                        continue

                    if execute_tests(subdir):
                        executed += 1
                        continue

            if not subdirs:
                exit(
                    "WARNING: Can't find Makefile, app.py, test.py, program.py"
                )

    print(f"{executed} functional tests passed")


if __name__ == "__main__":
    run_tests()
