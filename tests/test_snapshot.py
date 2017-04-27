from connections.nova_connection import NovaConnection
from connections.connection import AuthenticationV3
from migration.snapshot import make_snapshot
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass()}
    auth = AuthenticationV3(**creds)
    nova_creds = {"region_name": "-1",
                  "version": "2",
                  "authentication_v3": auth}
    regions = list(auth.compute_region)
    find = False
    while not find:
        print("region")
        print('\n'.join('=> ' + str(region) for region in regions))
        nova_creds["region_name"] = input("make a region choice: ")
        if nova_creds["region_name"] in regions:
            find = True
    ovh_nova_connection = NovaConnection(**nova_creds)
    make_snapshot(ovh_nova_connection, "arch_openstack", "test_v3")


if __name__ == '__main__':
    main()
