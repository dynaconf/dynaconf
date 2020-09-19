#!/usr/bin/env bash
# coding=utf-8
#
# Release a new version of Dynaconf.
#
# Test Dynaconf for sanity. If all is well, generate a new commit, tag it,
# and print instructions for further steps to take.
#
# NOTE: This script should be run from the repository root directory.
set -euo pipefail

# Check Requirements
if ! gitchangelog -v > /dev/null; then
  echo 'gitchangelog is required: "pip install -U gitchangelog"'
  exit 1
fi

if ! git --version > /dev/null; then
  echo 'git is required'
  exit 1
fi

if ! pre-commit --version > /dev/null; then
  echo 'pre-commit is required'
  exit 1
fi

if ! python3 -V > /dev/null; then
  echo 'python3 is required'
  exit 1
fi

if ! python -m wheel --help > /dev/null; then
  echo 'python-wheel is required'
  exit 1
fi

if ! twine --help > /dev/null; then
  echo 'twine is required'
  exit 1
fi

# See: http://mywiki.wooledge.org/BashFAQ/028
readonly script_name='release.sh'

# Print usage instructions to stdout.
show_help() {
fmt <<EOF
Usage: $script_name [options] <new-version>

Release a new version of Dynaconf. More specifically, write <new-version> to
the dynaconf/VERSION file, build new packages, test them for sanity, generate a new
tagged commit, and print instructions for next steps.

Options:
    --help
        Show this message.
    --repo-path
        The path to the root of the Dynaconf repository. Defaults to '.'.
EOF
}

# Transform $@. $temp is needed. If omitted, non-zero exit codes are ignored.
temp=$(getopt \
    --options '' \
    --longoptions help,repo-path: \
    --name "$script_name" \
    -- "$@")
eval set -- "$temp"
unset temp

# Read arguments. (getopt inserts -- even when no arguments are passed.)
if [ "${#@}" -eq 1 ]; then
    show_help
    exit 1
fi
while true; do
    case "$1" in
        --help) show_help; shift; exit 0;;
        --repo-path) cd "$2"; shift 2;;
        --) shift; break;;
        *) echo "Internal error! Encountered unexpected argument: $1"; exit 1;;
    esac
done
new_version="$1"; shift

old_version="$(git describe --tags "$(git rev-list --tags --max-count=1)")"  # e.g. 1.1.0
if [ "${new_version}" = "${old_version}" ]; then
    echo Nothing to release!
    exit 1
fi

# Generate new packages.
echo "${new_version}" > dynaconf/VERSION

# update doc header
sed -i "s/Dynaconf - [[:digit:]]*.[[:digit:]]*.[[:alnum:]]*/Dynaconf - ${new_version}/" mkdocs.yml

make dist
echo 'New Package generated!'
# Create a venv, and schedule it for deletion.
cleanup() { if [ -n "${venv:-}" ]; then rm -rf "${venv}"; fi }
trap cleanup EXIT  # bash pseudo signal
trap 'cleanup ; trap - SIGINT ; kill -s SIGINT $$' SIGINT
trap 'cleanup ; trap - SIGTERM ; kill -s SIGTERM $$' SIGTERM
venv="$(mktemp --directory)"
python3 -m venv "${venv}"

# Sanity check the new packages.
set +u
source "${venv}/bin/activate"
set -u
pip install --upgrade pip
for dist in dist/*; do
    pip install --quiet "${dist}"
    dynaconf list --help 1>/dev/null
    pip uninstall --quiet --yes dynaconf
done
set +u
deactivate
set -u
echo "Starting release of $new_version"

# ensure pre-commit is ok
make setup-pre-commit

# Create a new commit and annotated tag.
git add dynaconf/VERSION mkdocs.yml
pre-commit run --files dynaconf/VERSION mkdocs.yml || true

commit_message="$(git shortlog "${old_version}.." | sed 's/^./    &/')"
git commit \
    --message "Release version ${new_version}" \
    --message "Shortlog of commits since last release:" \
    --message "${commit_message}"
git tag --annotate "${new_version}" --message "Dynaconf ${new_version}" \
    --message "${commit_message}"

# Update changelog file
git rm -f CHANGELOG.md
gitchangelog > CHANGELOG.md
pre-commit run --files CHANGELOG.md || true
git add -f CHANGELOG.md
git commit --amend --no-edit

fmt <<EOF

This script has made only local changes: it has updated the dynaconf/VERSION file,
generated the CHANGELOG.md file and a new commit, tagged the new commit, and performed
a few checks along the way. If you are confident in these changes, you can publish them with
commands like the following:
EOF

cat <<EOF

    git push --tags origin master
    make publish
    hub release create ${new_version} -m "${new_version}"

EOF
