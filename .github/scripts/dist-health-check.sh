#!/bin/env bash

set -euo pipefail
echo "Checking dist build health"

venv="$(mktemp --directory)"
python3 -m venv "${venv}"
source "${venv}/bin/activate"

for dist in dist/*; do
    pip install --quiet "${dist}"
    dynaconf list --help 1>/dev/null
done

deactivate
rm -rf "${venv}"
echo "Done"
