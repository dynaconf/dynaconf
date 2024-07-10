#!/bin/bash
docker run --rm --name dynaconf_with_redis -d -p 6379:6379 redis:alpine || true
sleep 2
cd tests_functional/legacy/redis_example
pwd
dynaconf -i dynaconf.settings write redis -s FOO=foo_is_default
dynaconf -i dynaconf.settings write redis -s SECRET=redis_works_in_default
dynaconf -i dynaconf.settings write redis -e development -s SECRET=redis_works_in_development
dynaconf -i dynaconf.settings write redis -e production -s SECRET=redis_works_in_production
sleep 2
python redis_example.py
docker stop dynaconf_with_redis || true
cd ../../../
