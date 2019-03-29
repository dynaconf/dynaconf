#!/usr/bin/env sh
export DYNACONF_SETTINGS=dynaconf.test_settings
export DYNATRAVIS_ENV_BOOLEAN='@bool true'
export DYNATRAVIS_ENV_INT='@int 42'
export DYNATRAVIS_ENV_FLOAT='@float 42.2'
export DYNATRAVIS_ENV_LIST='@json ["dyna", "conf"]'
export DYNATRAVIS_ENV_DICT='@json {}'
export DYNATRAVIS_ENV_PURE_INT=42
export DYNATRAVIS_ENV_STR_INT="'42'"
export OTHER_TESTING='@bool yes'
export OTHER_ENABLED=true
export OTHER_DISABLED=false
