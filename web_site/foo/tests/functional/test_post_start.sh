#!/usr/bin/env bash

if [ $# -ne 7 ]; then
exit 42
fi

ADDRESS_PORT=$1
ID=$2
REGION_SRC=$3
MACHINE_NAME_SRC=$4
REGION_DEST=$5
MACHINE_NAME_DEST=$6
FLAVOR=$7

generate_post_data()
{
cat << EOF
{
"from": {"region": "$REGION_SRC", "machine_name": "$MACHINE_NAME_SRC"},
"to": {"region": "$REGION_DEST", "machine_name": "$MACHINE_NAME_DEST", "flavor": "$FLAVOR"}
}
EOF
}

curl -X POST ${ADDRESS_PORT}/v6/migrate/${ID}/start -H 'Content-Type: application/json' -d "$(generate_post_data)"
