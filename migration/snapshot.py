from connections.nova_connection import NovaConnection
from utils.get_ids import get_server_id_from_nova


def make_snapshot(nova_connection: NovaConnection, server_name: str, snapshot_name: str):
    server_id = get_server_id_from_nova(nova_connection, server_name)
    if len(server_id) == 0:
        raise ValueError("We don't have found this following server " + server_name)

    # TODO make a user choice here
    server_uuid = server_id[0]
    make_snapshot_from_uuid(nova_connection, server_uuid, snapshot_name)


def make_snapshot_from_uuid(nova_connection: NovaConnection, server_uuid: str, snapshot_name: str):
    # Can raise a nova_exception.Conflict if there have multiple snap from the same server name
    try:
        snapshot_image_uuid = nova_connection.connection.servers.create_image(server_uuid, snapshot_name)
    except nova_connection.Conflict:
        raise

    # TODO make a thread ? a signal ? sleep call ?
    # TODO make a timeout mode
    # TODO (test) make multi read and multi write
    is_active = False
    while not is_active:
        image_info = dict(nova_connection.connection.glance.find_image(snapshot_image_uuid).to_dict())
        if 'status' in image_info and image_info['status'] == "active":
            is_active = True
