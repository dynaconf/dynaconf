#!/bin/bash
#
# This prepares for the release by:
# - updating the changelog
# - bumping version files to the final release version (e.g, x.y.z without .dev)

set -euo pipefail

# {major}.{minor}.{patch}-{pre}.{pre_n}
# e.g: 3.2.5-dev0 -> 3.2.5
echo "[BUMP] Bumping files for distribution version: x.y.z-dev0 -> x.y.z"
bump-my-version bump pre

# update changelog in-place with current_version (e.g: 3.2.5-dev0)
echo "[BUMP] Updating changelog"
CURRENT_VERSION="$(bump-my-version show current_version)"
git-changelog --bump "${CURRENT_VERSION:?is-empty}"

echo "[BUMP] Done."
