from connections.nova_connection import OVHNovaConnection
from migration.snapshot import make_snapshot


def main():
    ovh_nova_connection = OVHNovaConnection()
    ovh_nova_connection.ask_credentials()
    ovh_nova_connection.region_name = "GRA3"
    ovh_nova_connection.connect()
    make_snapshot(ovh_nova_connection, "arch_openstack", "refactor_src")

if __name__ == '__main__':
    main()
