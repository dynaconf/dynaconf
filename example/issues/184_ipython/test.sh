#!/bin/bash
python app.py || exit 1

pushd subdir
python app.py || exit 1
popd


ipython app.py || exit 1

pushd subdir
ipython app.py || exit 1
popd
