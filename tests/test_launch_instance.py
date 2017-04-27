from connections.nova_connection import NovaConnection
from connections.neutron_connection import NeutronConnection
from migration.launch_instance import launch_instance
from utils.get_ids import get_ovh_default_nics
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "region_name": "BHS3",
             "version": "2"}
    ovh_nova_connection = NovaConnection(**creds)
    ovh_neutron_connection = NeutronConnection(**creds)
    launch_instance(ovh_nova_connection, "refactor_instance", "test_ovh_snap_and_migration_dest", "s1-4",
                    get_ovh_default_nics(ovh_neutron_connection))


if __name__ == '__main__':
    main()
