from connections.nova_connection import OVHNovaConnection
from connections.neutron_connection import OVHNeutronConnection
from migration.launch_instance import launch_instance
from utils.get_nics import get_ovh_default_nics


def main():
    ovh_nova_connection = OVHNovaConnection()
    ovh_nova_connection.authentication.project_id = input("Project id: ")
    ovh_nova_connection.authentication.username = input("Username: ")
    ovh_nova_connection.authentication.password = input("Password: ")
    ovh_nova_connection.authentication['region_name'] = "BHS3"
    ovh_nova_connection.connect()

    ovh_neutron_connection = OVHNeutronConnection()
    ovh_neutron_connection.authentication.project_id = ovh_nova_connection.authentication.project_id
    ovh_neutron_connection.authentication.password = ovh_nova_connection.authentication.password
    ovh_neutron_connection.authentication.username = ovh_nova_connection.authentication.username
    ovh_neutron_connection.authentication['region_name'] = "BHS3"
    ovh_neutron_connection.authentication['version'] = "2.0"
    ovh_neutron_connection.connect()

    launch_instance(ovh_nova_connection, input("Instance name: "), input("Snapshot name: "), input("Flavor name: "), input("Network id: "))

if __name__ == '__main__':
    main()
