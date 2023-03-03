#!/bin/bash
export SETTINGS_FILE_FOR_DYNACONF=$(mktemp --suffix .yaml)
echo "offset: 24" > $SETTINGS_FILE_FOR_DYNACONF
PARENT=$(realpath .)
mkdir nonexistent_dir
cd nonexistent_dir
rm -r ../nonexistent_dir
ls ../
python $PARENT/app.py
cat $SETTINGS_FILE_FOR_DYNACONF
rm -r $SETTINGS_FILE_FOR_DYNACONF
