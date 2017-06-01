from connections.nova_connection import NovaConnection


def attach_volumes(nova_connection: NovaConnection, server_id: str, volumes_id: list):
    for volume in volumes_id:
        attach_a_volume(nova_connection, server_id, volume)


def attach_a_volume(nova_connection: NovaConnection, server_id: str, volume_id: str):
    nova_connection.connection.volumes.create_server_volume(server_id, volume_id)
