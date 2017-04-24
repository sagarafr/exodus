from connections.openstack_connection import OVHOpenStackConnection


def init_project_and_connection():
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.authentication.ask_credentials()
    ovh_openstack_connection.profile = "SBG3"
    ovh_openstack_connection.connect()
    return ovh_openstack_connection


def print_element(ovh_os_co):
    print("ovh_os_co.authentication", ovh_os_co.authentication)
    print("ovh_os_co.token", ovh_os_co.token)


def main():
    ovh_os_co = init_project_and_connection()
    print_element(ovh_os_co)


if __name__ == '__main__':
    main()
