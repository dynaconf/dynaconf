#!/usr/bin/env sh
py.test -v --cov-config .coveragerc --cov=dynaconf -l tests/ --junitxml=junit/test-results.xml
