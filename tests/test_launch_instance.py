from connections.nova_connection import OVHNovaConnection
from connections.neutron_connection import OVHNeutronConnection
from migration.launch_instance import launch_instance
from utils.get_nics import get_ovh_default_nics


def main():
    ovh_nova_connection = OVHNovaConnection()
    ovh_nova_connection.authentication.project_id = "3ca82ba8531844098e8bfdeacc7a312d"
    ovh_nova_connection.authentication.username = "5nqy3925tFRf"
    ovh_nova_connection.authentication.password = "JTUEdZPthATfSSKf34GDKdD92Uk6xjHG"
    ovh_nova_connection.authentication['region_name'] = "BHS3"
    ovh_nova_connection.connect()

    ovh_neutron_connection = OVHNeutronConnection()
    ovh_neutron_connection.authentication.project_id = ovh_nova_connection.authentication.project_id
    ovh_neutron_connection.authentication.password = ovh_nova_connection.authentication.password
    ovh_neutron_connection.authentication.username = ovh_nova_connection.authentication.username
    ovh_neutron_connection.authentication['region_name'] = "BHS3"
    ovh_neutron_connection.authentication['version'] = "2.0"
    ovh_neutron_connection.connect()

    launch_instance(ovh_nova_connection, "refactor", "refactor", "s1-4", "bf8869ea-aaba-4a34-b7e9-9010861ff5f6")

if __name__ == '__main__':
    main()
