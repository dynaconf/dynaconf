#!/bin/bash

# read this before running it, its very dumb and won't handle errors, and is provided as a raw suggestion

# this is meant to be run from the local directory

echo "========== Creating .venv =========="
python3.8 -m venv .venv
source .venv/bin/activate
type python
pip install -Uq pip
pip install -q dynaconf==3.1.7
echo "========== Printing value in dynaconf 3.1.7 =========="
python -c 'from config import settings; print(settings.nested.test_field)'
python -c 'from config import settings; print(settings.nested.group_field)'

pip install -q dynaconf==3.1.8
echo "========== Printing value in dynaconf 3.1.8 =========="
python -c 'from config import settings; print(settings.nested.test_field)'
python -c 'from config import settings; print(settings.nested.group_field)'
