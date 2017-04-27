from utils.find_flavors import find_flavors
from utils.get_ids import get_image_from_nova
from connections.nova_connection import NovaConnection


def launch_instance(nova_connection: NovaConnection, instance_name: str,
                    snapshot_name: str, flavor: str, network: list):
    image = get_image_from_nova(nova_connection, snapshot_name)[0]
    flavor_uuid = find_flavors(nova_connection, flavor)[0]
    nova_connection.connection.servers.create(instance_name, image, flavor_uuid, nics=network)
