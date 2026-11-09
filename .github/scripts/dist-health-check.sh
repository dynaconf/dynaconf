#!/bin/env bash

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "Checking dist build health"

for dist in dist/*; do
    uv run --isolated --with "${dist}" -- dynaconf list --help 1>/dev/null
done

echo "Done"
