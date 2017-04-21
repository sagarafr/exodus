from connections.openstack_connection import OVHOpenStackConnection
from connections.openstack_project import OpenStackProject


def opensctack_connection():
    ovh_openstack_connection = OVHOpenStackConnection()
    openstack_project = OpenStackProject()
    openstack_project.ask_credentials()
    ovh_openstack_connection.import_credentials(openstack_project)
    ovh_openstack_connection.connect()
    print(ovh_openstack_connection.authenticator)
    print(ovh_openstack_connection.connection.authenticator)


def openstack_connection_ask():
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.ask_credentials()
    ovh_openstack_connection.connect()
    print(ovh_openstack_connection.authenticator)
    print(ovh_openstack_connection.connection.authenticator)


def main():
    opensctack_connection()
    openstack_connection_ask()


if __name__ == '__main__':
    main()
