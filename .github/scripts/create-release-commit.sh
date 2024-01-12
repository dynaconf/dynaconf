#!/bin/bash

# ensure pre-commit is ok
make setup-pre-commit

# Create a new commit and annotated tag.
git add dynaconf/VERSION mkdocs.yml CHANGELOG.md
pre-commit run --files dynaconf/VERSION mkdocs.yml || true

commit_message="$(git shortlog "${old_version}.." | sed 's/^./    &/')"
git commit \
    --message "Release version ${new_version}" \
    --message "Shortlog of commits since last release:" \
    --message "${commit_message}"
git tag --annotate "${new_version}" --message "Dynaconf ${new_version}" \
    --message "${commit_message}"

