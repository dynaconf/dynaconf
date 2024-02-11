#!/bin/bash

set -eu -o pipefail

NEW_VERSION="$1"
OLD_VERSION="$(git describe --tags --abbrev=0)"
echo "NEW_VERSION=$NEW_VERSION"
echo "OLD_VERSION=$OLD_VERSION"

# Check NEW_VERSION > OLD_VERSION
echo "Checking NEW_VERSION > OLD_VERSION"
python -c "import semver; exit(not semver.version.Version.parse('$NEW_VERSION').compare('$OLD_VERSION') > 0)"

# Create a new commit
echo "Creating tagged release commit"
git add dynaconf/VERSION mkdocs.yml CHANGELOG.md
commit_message="$(git shortlog "${OLD_VERSION}.." | sed 's/^./    &/')"
git commit \
    --message "Release version ${NEW_VERSION}" \
    --message "Shortlog of commits since last release:" \
    --message "${commit_message}"

# Add lightweight tag
git tag "${NEW_VERSION}"
