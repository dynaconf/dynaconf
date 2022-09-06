#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dynaconf.vendor.tomllib import load


def run_tests():
    root_directory = Path(__file__).parent
    print("Workdir:", root_directory.absolute())
    functional_tests = sorted(list(root_directory.iterdir()))
    print("Collected functional tests:", len(functional_tests))
    for path in functional_tests:
        if path.is_dir():
            if path.name in [".", "__pycache__"]:
                continue
            print("-" * 80)
            print("Starting Test on:", path)

            env = {**os.environ}
            if os.path.exists(path / "env.toml"):
                print("Loading env.toml")
                _envvars = load(open(path / "env.toml", "rb"))
                env.update(_envvars)

            if (path / "Makefile").exists():
                print("Running make")
                subprocess.check_call(["make", "test"], cwd=path, env=env)
                continue

            if (path / "app.py").exists():
                print("Running app.py")
                subprocess.check_call(
                    [sys.executable, "app.py"], cwd=path, env=env
                )
                continue

            if (path / "program.py").exists():
                print("Running program.py")
                subprocess.check_call(
                    [sys.executable, "program.py"], cwd=path, env=env
                )
                continue

            if (path / "test.py").exists():
                print("Running test.py")
                subprocess.check_call(
                    [sys.executable, "test.py"], cwd=path, env=env
                )
                continue

            exit("WARNING: Can't find Makefile, app.py, test.py, program.py")

    print("All Functional tests passed")


if __name__ == "__main__":
    run_tests()
