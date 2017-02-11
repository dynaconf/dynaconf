#!/usr/bin/env bash
#export DYNACONF_SETTINGS=dynaconf.test_settings
export TRAVIS=true
export DYNATRAVIS_ENV_BOOLEAN='@bool true'
export DYNATRAVIS_ENV_INT='@int 42'
export DYNATRAVIS_ENV_FLOAT='@float 42.2'
export DYNATRAVIS_ENV_LIST='@json ["dyna", "conf"]'
# - DYNATRAVIS_ENV_DICT='@json {"dyna": "conf"}' how to fix this?
export DYNATRAVIS_ENV_DICT='@json {}'
export DYNATRAVIS_ENV_PURE_INT=42
export OTHER_TESTING='@bool yes'