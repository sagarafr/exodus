#!/usr/bin/env bash

if [ $# -ne 1 ]; then
exit 42
fi

ADDRESS_PORT=$1
FILENAME=`pwd`/web_site/foo/tests/functional/openstack_rc.sh

curl i -X POST -F file=@/home/mgappa/documents/dev/exodus/web_site/foo/tests/functional/openstack_rc.sh ${ADDRESS_PORT}/v6/migrate --verbose
