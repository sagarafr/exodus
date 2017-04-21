from connections.nova_connection import NovaConnection
from utils.find_flavors import find_flavors


def launch_instance(nova_connection: NovaConnection, instance_name: str,
                    snapshot_name: str, flavor: str, network: str):
    print(nova_connection.authentication, network)
    image_uuid = nova_connection.connection.glance.find_image(snapshot_name)
    flavor_uuid = find_flavors(nova_connection, flavor)[0]
    nova_connection.connection.servers.create(instance_name, image_uuid, flavor_uuid, nics_id=network)
