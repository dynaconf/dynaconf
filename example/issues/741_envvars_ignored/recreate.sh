#!/bin/bash
export TESTING_nested__test_field=setbyenv
export TESTING_nested__group_field=setbyenvgroup
python -c 'from app import settings; assert settings.nested.test_field == "setbyenv"'
python -c 'from app import settings; assert settings.nested.group_field == "setbyenvgroup"'
