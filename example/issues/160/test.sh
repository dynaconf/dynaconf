#!/bin/bash
echo 'Testing: Regression on config path-traversal #160'
python -c "from dynaconf import settings; print(settings.ENV_FOR_DYNACONF)" | grep testissue160 || exit 1

pushd subfolder
python -c "from dynaconf import settings; print(settings.ENV_FOR_DYNACONF)" | grep testissue160 || exit 1
popd
