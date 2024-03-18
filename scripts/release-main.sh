#/bin/bash
#
# This is the entrypoint for doing a manual release

echo "[RELEASE] Checking pre-conditions."
if [[ -n "$(git status -s)" ]]; then echo "You shouldn't have unstaged changes."; exit 1; fi
if [[ ! -d ".git" ]]; then echo "You should run from the repository root dir."; exit 1; fi
if [[ $(git rev-parse --abbrev-ref HEAD) != "master" ]]; then echo "Should be on master branch."; exit 1; fi

echo "[RELEASE] Starting release process."
set -euo pipefail

make run-pre-commit
make run-tox

scripts/_release-prepare-bumps.sh
scripts/_release-build-dist.sh
scripts/_release-create-commits.sh

echo "[RELEASE] Done."

fmt <<EOF

This script has made only local changes:

- Created a release-commit (tagged w/ release version):
  * Updated the CHANGELOG.md
  * Updated version files for release: x.y.z-dev0 -> x.y.z
    - dynaconf/VERSION, mkdocs.yml, .bumpversion.toml
- Created a bump-commit:
  * Updated version files for next dev cycle : x.y.z -> x.y.next-dev0
- Built and checked new distribution:
  * Packages should be in 'dist/*'


If you are confident with the changes:

1. Publish the distribution packages
2. Manually create a release on Github


Publish snippet:

git push --tags git@github.com:dynaconf/dynaconf master
make publish

EOF
