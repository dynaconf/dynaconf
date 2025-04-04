#!/bin/bash

set -euo pipefail

# Ensure we are using a python lowerbound version
PYTHON_LOWERBOUND=$(python -c \
   'import toml; \
   data=toml.load("pyproject.toml"); \
   version=data["project"]["requires-python"].split("=")[-1]; \
   print(version)' \
)

PYTHON_ERR_MSG="$(cat <<EOF
ERROR: Must use python ${PYTHON_LOWERBOUND}
Minification creates code compatible with the current python version in use.
For greater compatibility, the build should be done with the lower python we support.\n
EOF
)"

if ! python --version | grep $PYTHON_LOWERBOUND; then
   printf "$PYTHON_ERR_MSG"
   exit 1
fi

# Ensure vendor is source and cleanup vendor_src backup folder
ls dynaconf/vendor/source && rm -rf dynaconf/vendor_src

# Backup dynaconf/vendor folder as dynaconf/vendor_src
mv dynaconf/vendor dynaconf/vendor_src

# Ensure main vendor directory exists
mkdir -p dynaconf/vendor

# Ensure there is an __init__.py file in the vendor directory
touch dynaconf/vendor/__init__.py

# copy the vendor.txt file to vendor directory
cp dynaconf/vendor_src/vendor.txt dynaconf/vendor/vendor.txt

# For each folder in vendor_src
for direc in box click dotenv ruamel/yaml toml tomllib
do

   # Ensure that the directory exists.
   mkdir -p dynaconf/vendor/$direc
   # Ensure there is an __init__.py file.
   touch dynaconf/vendor/$direc/__init__.py

   # for each .py file in the vendor_srx directory
   # NOTE: vendor_src is created when make minify_vendor is run
   for eachfile in `ls dynaconf/vendor_src/$direc/*.py`
   do
      # minify each file pasting resilts to the dynaconf/vendor directory
      pyminify --remove-literal-statements $eachfile > ${eachfile/_src/''}
   done

   for eachfile in `ls dynaconf/vendor_src/$direc/{*.{typed,rst,in,cfg,md},CHANGES,LICENSE,PKG-INFO}`
   do
      # copy each file to the dynaconf/vendor directory
      cp $eachfile ${eachfile/_src/''}
   done

done

# Ensure ruamel/__init__.py exists
touch dynaconf/vendor/ruamel/__init__.py
