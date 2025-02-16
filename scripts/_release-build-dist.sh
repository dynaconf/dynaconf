#!/bin/bash
#
# This build and test (health-check) a distribution:

set -euo pipefail

echo '[BUILD] Building new package distribution.'

make dist

# Create a venv, and schedule it for deletion.
echo '[BUILD] Testing package distribution'
cleanup() { if [ -n "${venv:-}" ]; then rm -rf "${venv}"; fi }
trap cleanup EXIT  # bash pseudo signal
trap 'cleanup ; trap - SIGINT ; kill -s SIGINT $$' SIGINT
trap 'cleanup ; trap - SIGTERM ; kill -s SIGTERM $$' SIGTERM
venv="$(mktemp --directory)"
# ensure the running version of Python is < 3.12 (for compatibility)
# else exit with an error message.
# The reason is that pyminify generates minified code that is compatible only with the 
# running Python version. So, if the code is minified with Python 3.12, it will not be
# compatible with Python <3.12.
python3.11 -m venv "${venv}"

# Sanity check the new packages.
set +u
source "${venv}/bin/activate"
set -u
pip install --upgrade pip
for dist in dist/*; do
    pip install --quiet "${dist}"
    dynaconf list --help 1>/dev/null
    pip uninstall --quiet --yes dynaconf
done
set +u
deactivate
set -u

echo "[BUILD] Done."
