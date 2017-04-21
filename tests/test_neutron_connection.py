from connections.neutron_connection import OVHNeutronConnection


def main():
    ovh_neutron_connection = OVHNeutronConnection()
    ovh_neutron_connection.ask_credentials()
    ovh_neutron_connection.connect()
    print(ovh_neutron_connection.authentication)
    print(ovh_neutron_connection.connection.list_networks())


if __name__ == '__main__':
    main()
