#!/bin/bash -x
export SETTINGS_FILE_FOR_DYNACONF=$(mktemp -t dynaconf.XXXXX.yaml)
echo "offset: 24" > $SETTINGS_FILE_FOR_DYNACONF
PARENT=$(readlink -f .)
mkdir nonexistent_dir
cd nonexistent_dir
rm -r ../nonexistent_dir
ls ../
python $PARENT/app.py
cat $SETTINGS_FILE_FOR_DYNACONF
rm -r $SETTINGS_FILE_FOR_DYNACONF
