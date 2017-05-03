#!/usr/bin/env bash

if [ $# -ne 5 ]; then
exit 42
fi

ADDRESS_PORT=$1
USERNAME=$2
PASSWORD=$3
AUTH_URL=$4
TYPE=$5

generate_post_data()
{
cat << EOF
{
"from": {"username": "$USERNAME", "password": "$PASSWORD", "auth_url": "$AUTH_URL", "type": "$TYPE"},
"to": {"username": "$USERNAME", "password": "$PASSWORD", "auth_url": "$AUTH_URL", "type": "$TYPE"}
}
EOF
}

generate_post_error()
{
cat << EOF
{
"from": {"username": "$USERNAME", "password": "$PASSWORD", "auth_url": "$AUTH_URL", "type": "$TYPE"},
"a": {"username": "$USERNAME", "password": "$PASSWORD", "auth_url": "$AUTH_URL", "type": "$TYPE"},
"to": {"username": "$USERNAME", "password": "$PASSWORD", "auth_url": "$AUTH_URL", "type": "$TYPE"}
}
EOF
}

curl -X POST ${ADDRESS_PORT}/v6/migrate -H 'Content-Type: application/json' -d "$(generate_post_data)"
curl -X POST ${ADDRESS_PORT}/v6/migrate -H 'Content-Type: application/json' -d "$(generate_post_error)"
