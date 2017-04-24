from connections.openstack_connection import OVHOpenStackConnection


def openstack_connection_ask():
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.ask_credentials()
    ovh_openstack_connection.profile = "SBG3"
    ovh_openstack_connection.connect()
    print(ovh_openstack_connection.authenticator)
    print(ovh_openstack_connection.connection.authenticator)


def main():
    openstack_connection_ask()


if __name__ == '__main__':
    main()
