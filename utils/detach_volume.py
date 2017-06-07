from connections.nova_connection import NovaConnection
from utils.get_volume import get_volumes


def detach_all_volumes(nova_connection: NovaConnection, server_id: str):
    """
    Detach all volumes attached into server_id

    :param nova_connection: NovaConnection with the same region that server_id 
    :param server_id: str contain the id of one instance
    """
    for volume_id in get_volumes(nova_connection, server_id):
        detach_a_volume(nova_connection, server_id, volume_id)


def detach_a_volume(nova_connection: NovaConnection, server_id: str, volume_id: str):
    """
    Detach a volume attached into server_id

    :param nova_connection: NovaConnection with the same region that server_id and volume_id 
    :param server_id: str contain the id of one instance
    :param volume_id: str contain the id of one volume
    """
    nova_connection.connection.volumes.delete_server_volume(server_id, volume_id)
