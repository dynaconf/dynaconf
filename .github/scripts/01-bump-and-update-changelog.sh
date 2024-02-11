#!/bin/bash

set -eu -o pipefail

NEW_VERSION="$1"
echo "NEW_VERSION=$NEW_VERSION"

# Bump Version
echo "Bumping Version Files"
echo "${NEW_VERSION}" > dynaconf/VERSION
sed -i "s/Dynaconf - [[:digit:]]*.[[:digit:]]*.[[:alnum:]]*/Dynaconf - ${NEW_VERSION}/" mkdocs.yml

# Generate Changelog
echo "Generating Changelog"
git-changelog --bump "$NEW_VERSION"
