#!/bin/bash
#
# This creates commits related to the next release:
# - Create tagged release-commit.
# - Create bump-commit (prepare for the next dev cycle. E.g: 3.2.5 -> 3.2.6-dev0)

set -euo pipefail

# create release-commit
git add dynaconf/VERSION mkdocs.yml CHANGELOG.md

LATEST_RELEASE="$(bump-my-version show scm_info.current_version)"
NEW_VERSION="$(bump-my-version show current_version)"

COMMIT_TITLE="Release version ${NEW_VERSION}"
COMMIT_MSG="$(git shortlog "${LATEST_RELEASE}.." | sed 's/^./    &/')"
TAG_TITLE="${NEW_VERSION}"
TAG_MSG="Released in $(date -Idate) by $(git config user.name) <$(git config user.email)>"

git commit \
    --message "${COMMIT_TITLE}" \
    --message "Shortlog of commits since last release:" \
    --message "${COMMIT_MSG}"
git tag --annotate "${TAG_TITLE}" \
    --message "${TAG_MSG}" \

# create bump-commit
bump-my-version bump patch --commit
