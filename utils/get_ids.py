from keystoneauth1.identity import v3
from keystoneauth1.session import Session
from connections.nova_connection import NovaConnection
from connections.glance_connection import GlanceConnection
from connections.neutron_connection import NeutronConnection


def get_server_id_from_nova(nova_connection: NovaConnection, server_name: str):
    """
    Get the id of server_name from nova_connection region

    :param nova_connection: NovaConnection object use to make the request
    :param server_name: str server_name to find
    :return: list of server id of server_name
    """
    server_id = []
    for server in nova_connection.connection.servers.list():
        server_info = dict(server.to_dict())
        if 'name' in server_info and 'id' in server_info and server_name == server_info['name']:
            server_id.append(server_info['id'])
    return server_id


def get_snapshot_id_from_glance(glance_connection: GlanceConnection, snapshot_name: str):
    """
    Get the snapshot id of snapshot_name from glance_connection region

    :param glance_connection: GlanceConnection object use to make the request 
    :param snapshot_name: str snapshot_name to find
    :return: list of snapshot id of snapshot_name 
    """
    snapshot_id = []
    for snapshot in glance_connection.connection.images.list():
        snapshot_info = dict(snapshot)
        if 'name' in snapshot_info and 'id' in snapshot_info and snapshot_info['name'] == snapshot_name:
            snapshot_id.append(snapshot_info['id'])
    return snapshot_id


def get_network_id_from_neutron(neutron_connection: NeutronConnection, network_name: str):
    """
    Get the network of network_name from neutron_connection region

    :param neutron_connection: NeutronConnection object use to make the request 
    :param network_name: str network_name to find 
    :return: list of network if of network_name
    """
    network_id = []
    for key in neutron_connection.connection.list_networks().keys():
        for element in neutron_connection.connection.list_networks().get(key):
            if 'name' in element and 'id' in element and element['name'] == network_name:
                network_id.append(element['id'])
    return network_id


def get_image_from_nova(nova_connection: NovaConnection, image_name: str):
    """
    Get the image of image_name from nova_connection region
    
    :param nova_connection: NovaConnection object use to make the request
    :param image_name: str image_name to find
    :return: list of image id of image_name
    """
    image_id = []
    for image in nova_connection.connection.glance.list():
        image_info = dict(image.to_dict())
        if 'name' in image_info and 'id' in image_info and image_info['name'] == image_name:
            image_id.append(image)
    return image_id


# TODO check if its used otherwise remove it
def get_catalog(authentication: v3.Password, session: Session):
    """
    Get the catalog of session from authentication

    :param authentication: v3.Password use to make the request
    :param session: Session use to use to make the request
    :return: dict of catalog
    """
    access = authentication.get_access(session=session)
    if access.has_service_catalog():
        return access.__dict__['_data']['token']['catalog']


def get_nics(neutron_connection: NeutronConnection, nics_name: str):
    """
    Find and take first nics_name from neutron_connection for external connection

    :param neutron_connection: NeutronConnection use to make the request
    :param nics_name: str nics_name to find
    :return: list correctly formatted for the network (used inside launch_connection function)
    """
    return [{'net-id': get_network_id_from_neutron(neutron_connection, nics_name)[0]}]


# TODO make this different ?
def get_ovh_default_nics(neutron_connection: NeutronConnection):
    """
    Give the default nics for ovh Ext-Net connection (external connection)

    :param neutron_connection: NeutronConnection use to make the request
    :return: list correctly formatted for the network (used inside launch_connection function) 
    """
    return get_nics(neutron_connection, 'Ext-Net')


def get_flavor_id(nova_connection: NovaConnection, instance_name: str):
    instance_id_list = []
    for image in nova_connection.connection.servers.list():
        image_info = dict(image.to_dict())
        if 'flavor' in image_info and 'id' in image_info['flavor'] and 'name' in image_info and image_info['name'] == instance_name:
            instance_id_list.append(image_info['flavor']['id'])

    return instance_id_list
