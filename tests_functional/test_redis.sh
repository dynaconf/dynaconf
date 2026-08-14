#!/bin/bash
set -euo pipefail

CONTAINER_NAME="dynaconf_with_redis"

cleanup() {
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

start_redis() {
    docker run --rm \
        --name "$CONTAINER_NAME" -d \
        -p 6379:6379 \
        redis:alpine
}

wait_for_redis() {
    echo "Waiting for redis to be ready..."
    for _ in $(seq 1 15); do
        if docker exec "$CONTAINER_NAME" redis-cli ping 2>/dev/null | grep -q PONG; then
            echo
            echo "Redis is ready"
            return 0
        fi
        printf "."
        sleep 1
    done
    echo
    echo "Timed out waiting for redis" >&2
    exit 1
}

run_test() (
    cd tests_functional/legacy/redis_example
    pwd
    dynaconf -i dynaconf.settings write redis -s FOO=foo_is_default
    dynaconf -i dynaconf.settings write redis -s SECRET=redis_works_in_default
    dynaconf -i dynaconf.settings write redis -e development -s SECRET=redis_works_in_development
    dynaconf -i dynaconf.settings write redis -e production -s SECRET=redis_works_in_production
    python redis_example.py
)

main() {
    start_redis
    wait_for_redis
    run_test
}

main
