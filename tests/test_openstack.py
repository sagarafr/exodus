from connections.openstack_connection import OVHOpenStackConnection
from connections.openstack_project import OpenStackProject


def init_project_and_connection():
    openstack_project = OpenStackProject()
    openstack_project.ask_credentials()
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.authentication.import_authentication_from_project(openstack_project)
    ovh_openstack_connection.connect()
    openstack_project.token = ovh_openstack_connection.token
    return openstack_project, ovh_openstack_connection


def print_element(os_project, ovh_os_co):
    print("os_project", os_project.to_dict())
    print("ovh_os_co.authentication", ovh_os_co.authentication)
    print("ovh_os_co.token", ovh_os_co.token)


def main():
    os_project, ovh_os_co = init_project_and_connection()
    print_element(os_project, ovh_os_co)


if __name__ == '__main__':
    main()
