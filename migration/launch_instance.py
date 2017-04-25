from utils.find_flavors import find_flavors_v3
from utils.get_ids import get_image_from_nova_v3
from connections.nova_connection import NovaConnectionV3


def launch_instance_v3(nova_connection: NovaConnectionV3, instance_name: str,
                    snapshot_name: str, flavor: str, network: list):
    image = get_image_from_nova_v3(nova_connection, snapshot_name)[0]
    flavor_uuid = find_flavors_v3(nova_connection, flavor)[0]
    nova_connection.connection.servers.create(instance_name, image, flavor_uuid, nics=network)
