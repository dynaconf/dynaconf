#!/usr/bin/env sh
py.test --boxed -v --cov-config .coveragerc --cov=dynaconf -l tests/ --junitxml=junit/test-results.xml
