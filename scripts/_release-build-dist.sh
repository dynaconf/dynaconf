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
python3 -m venv "${venv}"

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
