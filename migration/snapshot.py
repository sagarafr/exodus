from novaclient import exceptions
from connections.nova_connection import NovaConnection
from utils.get_ids import get_server_id_from_nova
from time import sleep


def make_snapshot(nova_connection: NovaConnection, server_name: str, snapshot_name: str):
    """
    Make a snapshot_name of server_name in nova_connection region
    If there are a multiple server_name take the first one

    :param nova_connection: NovaConnection object 
    :param server_name: str represent the name of the server in nova_connection region
    :param snapshot_name: str represent the name of the snapshot
    :raise: ValueError if server_name not found
    :raise: nova_connection.Conflit: This append when we try to make a multiple snapshot of the server_uuid 
    """
    server_uuid = None
    try:
        server_uuid = get_server_id_from_nova(nova_connection, server_name)[0]
    except IndexError as index:
        raise ValueError(server_name + " server not found")

    try:
        make_snapshot_from_uuid(nova_connection, server_uuid, snapshot_name)
    except:
        raise


def make_snapshot_from_uuid(nova_connection: NovaConnection, server_uuid: str, snapshot_name: str):
    """
    Make a snapshot_name of server_uuid in nova_connection region

    :param nova_connection: NovaConnection object 
    :param server_uuid: str of uuid of server in nova_connection region
    :param snapshot_name: str represent the name of the snapshot
    :raise: nova_connection.Conflit: This append when we try to make a multiple snapshot of the server_uuid
    :raise: ValueError: Appends if the status of the image is not queue or not saving and not active
    """
    try:
        snapshot_image_uuid = nova_connection.connection.servers.create_image(server_uuid, snapshot_name)
    except exceptions.Conflict:
        raise

    step = {"queued", "saving", "active"}
    is_active = False
    while not is_active:
        image_info = dict(nova_connection.connection.glance.find_image(snapshot_image_uuid).to_dict())
        if 'status' in image_info:
            if not image_info['status'] in step:
                raise ValueError("Unknown status : " + image_info['status'])
            if image_info['status'] == "active":
                is_active = True
        # Useful for the CPU ?
        if not is_active:
            sleep(2)
