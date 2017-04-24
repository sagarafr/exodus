from connections.neutron_connection import OVHNeutronConnection
from connections.openstack_connection import OVHOpenStackConnection


def main():
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.ask_credentials()
    ovh_openstack_connection.connect()

    ovh_neutron_connection = OVHNeutronConnection()
    ovh_neutron_connection.import_credentials(ovh_openstack_connection.authentication)
    ovh_neutron_connection.connect()
    print(ovh_neutron_connection.connection.list_networks())


if __name__ == '__main__':
    main()
