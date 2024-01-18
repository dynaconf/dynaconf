#!/bin/bash

NEW_VERSION="$1"

# 1. Bump Version

echo "${NEW_VERSION}" > dynaconf/VERSION
sed -i "s/Dynaconf - [[:digit:]]*.[[:digit:]]*.[[:alnum:]]*/Dynaconf - ${NEW_VERSION}/" mkdocs.yml

# 2. Generate Changelog
git-changelog --bump "$NEW_VERSION" --in-place

# 3. Create a new commit and annotated tag.
git add dynaconf/VERSION mkdocs.yml CHANGELOG.md
make setup-pre-commit
pre-commit run --files dynaconf/VERSION mkdocs.yml || true

commit_message="$(git shortlog "${old_version}.." | sed 's/^./    &/')"
git commit \
    --message "Release version ${new_version}" \
    --message "Shortlog of commits since last release:" \
    --message "${commit_message}"
git tag --annotate "${new_version}" --message "Dynaconf ${new_version}" \
    --message "${commit_message}"

