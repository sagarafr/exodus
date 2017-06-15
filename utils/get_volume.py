from connections.nova_connection import NovaConnection


def get_volumes(nova_connection: NovaConnection, server_id: str):
    """    
    :param nova_connection: 
    :param server_id: 
    :return: Volumes id 
    """
    return [volume.to_dict()["id"] for volume in nova_connection.connection.volumes.get_server_volumes(server_id)]
