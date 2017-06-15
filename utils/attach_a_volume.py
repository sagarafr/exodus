from connections.nova_connection import NovaConnection


def attach_volumes(nova_connection: NovaConnection, server_id: str, volumes_id: list):
    """
    Attach volumes all volumes contained in volumes_id at the instance with id server_id
    
    :param nova_connection: NovaConnection are the connection in the same region that server_id instance and volumes_id
    :param server_id: str contain the id of the instance
    :param volumes_id: list contain id of volumes
    """
    for volume in volumes_id:
        attach_a_volume(nova_connection, server_id, volume)


def attach_a_volume(nova_connection: NovaConnection, server_id: str, volume_id: str):
    """
    Attach the volume volume_id at the server_id 
    
    :param nova_connection: NovaConnection connection in the same region that server_id ant the volume_id
    :param server_id: str contain the id of the instance
    :param volume_id: str contain the id of the volume
    """
    nova_connection.connection.volumes.create_server_volume(server_id, volume_id)
