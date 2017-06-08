from novaclient import exceptions
from connections.nova_connection import NovaConnection
from connections.cinder_connection import CinderConnection
from connections.glance_connection import GlanceConnection
from utils.get_ids import get_server_id_from_nova
from utils.get_ids import get_snapshot_id_from_glance
from time import sleep


def make_hard_disk_snapshot(cinder_connection: CinderConnection, glance_connection: GlanceConnection,
                            nova_connection: NovaConnection, volume_id: str, snapshot_name: str):
    """
    Make a snapshot named snapshot_name of volume_id in cinder_connection and glance_connection region
    If there are multiple snapshot id take the first one
    
    :param cinder_connection: CinderConnection object to upload the volume into an image 
    :param glance_connection: GlanceConnection object to id of volume image created previously
    :param nova_connection: NovaConnection object to check if the volume is active
    :param volume_id: str id of volume
    :param snapshot_name: str name of the snapshot created
    """
    cinder_connection.connection.volumes.upload_to_image(volume_id, True, snapshot_name, "bare", "qcow2")
    uuid_snap = None
    is_active = False
    while uuid_snap is None:
        try:
            uuid_snap = get_snapshot_id_from_glance(glance_connection, snapshot_name)[0]
        except IndexError:
            sleep(2)
    while not is_active:
        try:
            is_active = check_availability(nova_connection, uuid_snap)
        except:
            raise
        if not is_active:
            sleep(2)


def make_snapshot(nova_connection: NovaConnection, server_name: str, snapshot_name: str):
    """
    Make a snapshot named snapshot_name of server_name in nova_connection region
    If there are a multiple server_name take the first one

    :param nova_connection: NovaConnection object 
    :param server_name: str represent the name of the server in nova_connection region
    :param snapshot_name: str represent the name of the snapshot
    :raise: ValueError if server_name not found
    :raise: nova_connection.Conflit: This append when we try to make a multiple snapshot of the server_uuid 
    """
    try:
        server_uuid = get_server_id_from_nova(nova_connection, server_name)[0]
    except IndexError:
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
    is_active = False
    while not is_active:
        try:
            is_active = check_availability(nova_connection, snapshot_image_uuid)
        except:
            raise
        if not is_active:
            sleep(2)


def check_availability(nova_connection: NovaConnection, snapshot_image_uuid: str):
    """
    Check the availability of snapshot_image_uuid

    :param nova_connection: NovaConnection object 
    :param snapshot_image_uuid: str snapshot uuid to find
    :return: bool True if is found else False
    :raise: ValueError if the status is unknown
    """
    # TODO make an enum of step
    step = {"queued", "saving", "active"}
    image_info = dict(nova_connection.connection.glance.find_image(snapshot_image_uuid).to_dict())
    if 'status' in image_info:
        if not image_info['status'] in step:
            raise ValueError("Unknown status : " + image_info['status'])
        if image_info['status'] == "active":
            return True
    return False
