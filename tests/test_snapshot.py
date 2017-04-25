from connections.nova_connection import NovaConnectionV3
from connections.connection import AuthenticationV3
from migration.snapshot import make_snapshot_v3
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
    print(nova_creds)
    ovh_nova_connection = NovaConnectionV3(**nova_creds)
    make_snapshot_v3(ovh_nova_connection, input("Instance name: "), input("Snapshot name: "))


if __name__ == '__main__':
    main()
