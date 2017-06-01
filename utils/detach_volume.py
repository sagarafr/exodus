from connections.nova_connection import NovaConnection
from utils.get_volume import get_volumes


def detach_all_volumes(nova_connection: NovaConnection, server_id: str):
    for volume_id in get_volumes(nova_connection, server_id):
        detach_a_volume(nova_connection, server_id, volume_id)


def detach_a_volume(nova_connection: NovaConnection, server_id: str, volume_id: str):
    nova_connection.connection.volumes.delete_server_volume(server_id, volume_id)
