#!/bin/bash

make setup-pre-commit
NEW_VERSION="$1"
OLD_VERSION="$(git describe --tags --abbrev=0)"
echo "NEW_VERSION=$NEW_VERSION"
echo "OLD_VERSION=$OLD_VERSION"

# 1. Bump Version
echo "${NEW_VERSION}" > dynaconf/VERSION
sed -i "s/Dynaconf - [[:digit:]]*.[[:digit:]]*.[[:alnum:]]*/Dynaconf - ${NEW_VERSION}/" mkdocs.yml
pre-commit run --files dynaconf/VERSION mkdocs.yml || true

# 2. Generate Changelog
git-changelog --bump "$NEW_VERSION" --in-place --filter-commits "3.2.4~.."

# 3. Create a new commit
git add dynaconf/VERSION mkdocs.yml CHANGELOG.md
commit_message="$(git shortlog "${OLD_VERSION}.." | sed 's/^./    &/')"
git commit \
    --message "Release version ${OLD_VERSION}" \
    --message "Shortlog of commits since last release:" \
    --message "${commit_message}"

# 4. Add lightweight tag
git tag "${NEW_VERSION}"
