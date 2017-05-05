from connections.nova_connection import NovaConnection
from utils.get_ids import get_server_id_from_nova


def make_snapshot(nova_connection: NovaConnection, server_name: str, snapshot_name: str):
    """
    Make a snapshot_name of server_name in nova_connection region
    If there are a multiple server_name take the first one

    :param nova_connection: NovaConnection object 
    :param server_name: str represent the name of the server in nova_connection region
    :param snapshot_name: str represent the name of the snapshot
    """
    server_id = get_server_id_from_nova(nova_connection, server_name)
    if len(server_id) == 0:
        raise ValueError("We don't have found this following server " + server_name)

    # TODO make a user choice here
    server_uuid = server_id[0]
    make_snapshot_from_uuid(nova_connection, server_uuid, snapshot_name)


def make_snapshot_from_uuid(nova_connection: NovaConnection, server_uuid: str, snapshot_name: str):
    """
    Make a snapshot_name of server_uuid in nova_connection region

    :param nova_connection: NovaConnection object 
    :param server_uuid: str of uuid of server in nova_connection region
    :param snapshot_name: str represent the name of the snapshot
    :raise nova_connection.Conflit: This append when we try to make a multiple snapshot of the server_uuid
    """
    try:
        snapshot_image_uuid = nova_connection.connection.servers.create_image(server_uuid, snapshot_name)
    except nova_connection.Conflict:
        raise

    # TODO make a thread ? a signal ? sleep call ?
    # TODO make a timeout mode (I think there are 3 common status and 1 error)
    is_active = False
    while not is_active:
        image_info = dict(nova_connection.connection.glance.find_image(snapshot_image_uuid).to_dict())
        if 'status' in image_info and image_info['status'] == "active":
            is_active = True
