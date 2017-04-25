from keystoneauth1.identity import v3
from keystoneauth1.session import Session
from connections.nova_connection import NovaConnectionV3
from connections.glance_connection import GlanceConectionV3
from connections.neutron_connection import NeutronConnectionV3


def get_server_id_from_nova_v3(nova_connection: NovaConnectionV3, server_name: str):
    server_id = []
    for server in nova_connection.connection.servers.list():
        print(server)
        server_info = dict(server.to_dict())
        if 'name' in server_info and 'id' in server_info and server_name == server_info['name']:
            server_id.append(server_info['id'])
    return server_id


def get_snapshot_id_from_glance_v3(glance_connection: GlanceConectionV3, snapshot_name: str):
    snapshot_id = []
    for snapshot in glance_connection.connection.images.list():
        snapshot_info = dict(snapshot)
        if 'name' in snapshot_info and 'id' in snapshot_info and snapshot_info['name'] == snapshot_name:
            snapshot_id.append(snapshot_info['id'])
    return snapshot_id


def get_network_id_from_neutron_v3(neutron_connection: NeutronConnectionV3, network_name: str):
    network_id = []
    for key in neutron_connection.connection.list_networks().keys():
        for element in neutron_connection.connection.list_networks().get(key):
            if 'name' in element and 'id' in element and element['name'] == network_name:
                network_id.append(element['id'])
    return network_id


def get_image_from_nova_v3(nova_connection: NovaConnectionV3, image_name: str):
    image_id = []
    for image in nova_connection.connection.glance.list():
        image_info = dict(image.to_dict())
        if 'name' in image_info and 'id' in image_info and image_info['name'] == image_name:
            image_id.append(image)
    return image_id


def get_catalog(authentication: v3.Password, session: Session):
    access = authentication.get_access(session=session)
    if access.has_service_catalog():
        return access.__dict__['_data']['token']['catalog']


def get_nics_v3(neutron_connection: NeutronConnectionV3, nics_name: str):
    return [{'net-id': get_network_id_from_neutron_v3(neutron_connection, nics_name)[0]}]


def get_ovh_default_nics_v3(neutron_connection: NeutronConnectionV3):
    return get_nics_v3(neutron_connection, 'Ext-Net')
