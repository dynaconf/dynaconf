#!/bin/bash
docker run --rm \
    --name dynaconf_with_vault -d \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
    -p 8200:8200 \
    hashicorp/vault:latest \
    || true
sleep 5
cd tests_functional/vault_userpass
pwd
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
dynaconf -i dynaconf.settings write vault -s SECRET=vault_works_in_default -s FOO=foo_is_default
dynaconf -i dynaconf.settings write vault -e dev -s SECRET=vault_works_in_dev
dynaconf -i dynaconf.settings write vault -e prod -s SECRET=vault_works_in_prod
sleep 2
python vault_userpass_example.py
docker stop dynaconf_with_vault  || true
cd ../../
