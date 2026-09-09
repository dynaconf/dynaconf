#!/bin/bash

set -euo pipefail

# Ensure dynaconf/vendor_src is source and cleanup vendor folder
ls dynaconf/vendor_src/source && rm -rf dynaconf/vendor

# Restore dynaconf/vendor_src folder as dynaconf/vendor
mv dynaconf/vendor_src dynaconf/vendor
