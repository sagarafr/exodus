from connections.nova_connection import NovaConnection
from connections.glance_connection import GlanceConnection
from connections.neutron_connection import NeutronConnection


def get_server_id_from_nova(nova_connection: NovaConnection, server_name: str):
    server_id = []
    for server in nova_connection.connection.servers.list():
        server_info = dict(server.to_dict())
        if 'name' in server_info and 'id' in server_info and server_name == server_info['name']:
            server_id.append(server_info['id'])
    return server_id


def get_snapshot_id_from_glance(glance_connection: GlanceConnection, snapshot_name: str):
    snapshot_id = []
    for snapshot in glance_connection.connection.images.list():
        snapshot_info = dict(snapshot)
        if 'name' in snapshot_info and 'id' in snapshot_info and snapshot_info['name'] == snapshot_name:
            snapshot_id.append(snapshot_info['id'])
    return snapshot_id


def get_network_id_from_neutron(neutron_connection: NeutronConnection, network_name: str):
    network_id = []
    for key in neutron_connection.connection.list_networks().keys():
        for element in neutron_connection.connection.list_networks().get(key):
            if 'name' in element and 'id' in element and element['name'] == network_name:
                network_id.append(element['id'])
    return network_id


def get_subnet_id_from_neutron(neutron_connection: NeutronConnection, subnet_name: str):
    subnet_id = []
    for key in neutron_connection.connection.list_networks().keys():
        for element in neutron_connection.connection.list_networks().get(key):
            if 'name' in element and 'subnets' in element and element['name'] == subnet_name:
                subnet = element['subnets']
                if isinstance(subnet, list):
                    subnet_id += subnet
                else:
                    subnet_id.append(element['subnets'])
    return subnet_id


def get_image_from_nova(nova_connection: NovaConnection, image_name: str):
    image_id = []
    for image in nova_connection.connection.glance.list():
        image_info = dict(image.to_dict())
        if 'name' in image_info and 'id' in image_info and image_info['name'] == image_name:
            image_id.append(image)
    return image_id
