from connections.neutron_connection import NeutronConnection
from utils.get_ids import get_network_id_from_neutron


def get_nics(neutron_connection: NeutronConnection, nics_name: str):
    return [{'net-id': get_network_id_from_neutron(neutron_connection, nics_name)[0]}]


def get_ovh_default_nics(neutron_connection: NeutronConnection):
    return get_nics(neutron_connection, 'Ext-Net')
