from connections.nova_connection import NovaConnectionV3
from connections.neutron_connection import NeutronConnectionV3
from migration.launch_instance import launch_instance_v3
from utils.get_ids import get_ovh_default_nics_v3
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "region_name": "BHS3",
             "version": "2"}
    ovh_nova_connection = NovaConnectionV3(**creds)
    ovh_neutron_connection = NeutronConnectionV3(**creds)
    launch_instance_v3(ovh_nova_connection, "refactor_instance", "test_ovh_snap_and_migration_dest", "s1-4",
                       get_ovh_default_nics_v3(ovh_neutron_connection))


if __name__ == '__main__':
    main()
