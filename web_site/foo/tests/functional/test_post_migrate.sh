#!/usr/bin/env bash

if [ $# -ne 4 ]; then
exit 42
fi

ADDRESS_PORT=$1
USERNAME=$2
PASSWORD=$3
AUTH_URL=$4

generate_post_data()
{
  cat <<EOF
{
"username": "$USERNAME",
"password": "$PASSWORD",
"auth_url": "$AUTH_URL"
}
EOF
}


curl -X POST ${ADDRESS_PORT}/v6/migrate -H 'Content-Type: application/json' -d "$(generate_post_data)"
