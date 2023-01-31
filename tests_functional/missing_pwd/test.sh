#!/bin/bash

set -e

rm -rf /tmp/foobar
mkdir -p /tmp/foobar
cd /tmp/foobar
rm -rf /tmp/foobar

dynaconf -i config.settings list
RC=$?
exit $RC
