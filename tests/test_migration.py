from connections.glance_connection import OVHGlanceConnection
from connections.openstack_connection import OVHOpenStackConnection
from migration.migration import migration


def main():
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.ask_credentials()
    ovh_openstack_connection.connect()

    credentials = dict(ovh_openstack_connection.authentication.credentials_to_dict())
    credentials.update({'token': ovh_openstack_connection.token})
    ovh_glance_connection_source = OVHGlanceConnection(**credentials)
    ovh_glance_connection_source.region_name = "GRA3"
    ovh_glance_connection_source.connect()
    ovh_glance_connection_destination = OVHGlanceConnection(**credentials)
    ovh_glance_connection_destination.region_name = "BHS3"
    ovh_glance_connection_destination.connect()
    migration(ovh_glance_connection_source, ovh_glance_connection_destination,
              "test_ovh_snap_and_migration", "refactor", "qcow2", "bare")

if __name__ == '__main__':
    main()
