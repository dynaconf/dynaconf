#!/bin/bash
#
# This prepares for the release by:
# - updating the changelog
# - bumping version files to the final release version (e.g, x.y.z without .dev)
# - generating  build
# - commit changes with release tag

set -euo pipefail

make run-pre-commit

# update changelog in-place with current_version (e.g: 3.2.5-dev0)
git-changelog --bump "$(bump-my-version show current_version)"

# {major}.{minor}.{patch}-{pre}.{pre_n}
# e.g: 3.2.5-dev0 -> 3.2.5
bump-my-version bump pre

make dist
twine check dist/*
