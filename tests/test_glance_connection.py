from connections.glance_connection import OVHGlanceConnection
from connections.openstack_connection import OVHOpenStackConnection


def main():
    ovh_openstack_connection = OVHOpenStackConnection()
    ovh_openstack_connection.ask_credentials()
    ovh_openstack_connection.connect()

    credentials = dict(ovh_openstack_connection.authentication.credentials_to_dict())
    credentials.update({'token': ovh_openstack_connection.token})
    # TODO refactor this because it's not relevant to make a openstack connection just for a token ?
    ovh_glance_connection = OVHGlanceConnection(**credentials)
    ovh_glance_connection.region_name = "BHS3"
    ovh_glance_connection.connect()
    for image in ovh_glance_connection.connection.images.list():
        print(image)

if __name__ == '__main__':
    main()
