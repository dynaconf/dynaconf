#!/bin/bash
set -euo pipefail

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
source .env
./manage.py migrate
./manage.py collectstatic --noinput
./manage.py loaddata project/fixtures/admin.json
