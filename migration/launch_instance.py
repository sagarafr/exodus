from utils.find_flavors import find_flavors
from utils.get_ids import get_image_from_nova
from connections.nova_connection import NovaConnection


def launch_instance(nova_connection: NovaConnection, instance_name: str,
                    snapshot_name: str, flavor: str, network: list):
    """
    Launch a instance_name in function of the snapshot_name, flavor and network.
    Find the first element of snapshot_name and flavor

    :param nova_connection: NovaConnection of the instance
    :param instance_name: str that represent the name of the instance
    :param snapshot_name: str that represent the name of the snapshot
    :param flavor: str that represent the name of the flavor
    :param network: list content the nics representation of the network
    :raise: ValueError if snapshot_name or flavor not found
    """
    image, flavor_uuid = None, None
    try:
        image = get_image_from_nova(nova_connection, snapshot_name)[0]
    except IndexError as index:
        raise ValueError(snapshot_name + " snapshot not found")
    try:
        flavor_uuid = find_flavors(nova_connection, flavor)[0]
    except IndexError as index:
        raise ValueError(flavor + " flavor not found")
    nova_connection.connection.servers.create(instance_name, image, flavor_uuid, nics=network)
