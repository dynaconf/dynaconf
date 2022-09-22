#!/bin/bash
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
