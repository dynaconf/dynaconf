#!/bin/bash
# good=2fab499
# bad=f037746
# cli_commit=

pushd "/home/pedro-psb/dev/projects/dynaconf/tests_functional/django_example" &>/dev/null

echo ">>> dynaconf $@"
DJANGO_SETTINGS_MODULE=foo.settings PYTHONPATH=. dynaconf "$@"
exit_code="$?"

popd &>/dev/null

if [[ $exit_code == 0 ]]; then
	echo "success"
	exit 0
else
	echo "failure"
	exit 1
fi
