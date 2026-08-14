#!/bin/bash
set -euo pipefail

CONTAINER_NAME="dynaconf_with_vault_userpass"

cleanup() {
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

start_vault() {
    docker run --rm \
        --name "$CONTAINER_NAME" -d \
        -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
        -p 8200:8200 \
        hashicorp/vault:1.21
}

wait_for_vault() {
    echo "Waiting for vault to be ready..."
    for _ in $(seq 1 15); do
        if curl -sf -o /dev/null http://127.0.0.1:8200/v1/sys/health; then
            echo
            echo "Vault is ready"
            return 0
        fi
        printf "."
        sleep 1
    done
    echo
    echo "Timed out waiting for vault" >&2
    exit 1
}

setup_userpass_auth() (
    cd tests_functional/legacy/vault_userpass
    curl --header "X-Vault-Token: myroot" --request PUT --data '{"type": "userpass"}' http://127.0.0.1:8200/v1/sys/auth/userpass
    curl \
        --header "X-Vault-Token: myroot" \
        --request POST \
        --data @admin.hcl \
        http://localhost:8200/v1/sys/policy/admin
    curl \
        --header "X-Vault-Token: myroot" \
        --request POST \
        --data @payload.json \
        http://127.0.0.1:8200/v1/auth/userpass/users/user
)

run_test() (
    cd tests_functional/legacy/vault_userpass
    pwd
    dynaconf -i dynaconf.settings write vault -s SECRET=vault_works_in_default -s FOO=foo_is_default
    dynaconf -i dynaconf.settings write vault -e dev -s SECRET=vault_works_in_dev
    dynaconf -i dynaconf.settings write vault -e prod -s SECRET=vault_works_in_prod
    python vault_userpass_example.py
)

main() {
    start_vault
    wait_for_vault
    setup_userpass_auth
    run_test
}

main
