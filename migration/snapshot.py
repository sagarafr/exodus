import asyncio
from novaclient import exceptions
from connections.nova_connection import NovaConnection
from connections.cinder_connection import CinderConnection
from connections.glance_connection import GlanceConnection
from utils.get_ids import get_server_id_from_nova
from utils.get_ids import get_snapshot_id_from_glance
from utils.get_ids import get_snapshot_id_from_glance_asyncio
from time import sleep


def make_hard_disk_snapshot(cinder_connection: CinderConnection, glance_connection: GlanceConnection, nova_connection: NovaConnection, volume_id: str, snapshot_name: str):
    cinder_connection.connection.volumes.upload_to_image(volume_id, True, snapshot_name, "bare", "qcow2")
    uuid_snap = None
    is_active = False
    timeout = 0
    while uuid_snap is None:
        try:
            uuid_snap = get_snapshot_id_from_glance(glance_connection, snapshot_name)[0]
        except Exception:
            timeout += 1
            if timeout < 5:
                sleep(2)
            else:
                raise
    while not is_active:
        try:
            is_active = check_availability(nova_connection, uuid_snap)
        except:
            raise
        if not is_active:
            sleep(2)


@asyncio.coroutine
def make_hard_disk_snapshot_asyncio(cinder_connection: CinderConnection, glance_connection: GlanceConnection,
                                    nova_connection: NovaConnection, volume_id: str, snapshot_name: str):
    cinder_connection.connection.volumes.upload_to_image(volume_id, True, snapshot_name, "bare", "qcow2")
    is_active = False
    uuid_snap = yield from asyncio.ensure_future(get_uuid_snapshot_asyncio(glance_connection, snapshot_name))
    if uuid_snap is None:
        raise Exception("Can't find snapshot uuid")
    while not is_active:
        try:
            is_active = yield from asyncio.ensure_future(check_availability_asyncio(nova_connection, uuid_snap))
        except:
            raise


# TODO add a time out
@asyncio.coroutine
def get_uuid_snapshot_asyncio(glance_connection: GlanceConnection, snapshot_name: str):
    uuid_snap = None
    while uuid_snap is None:
        try:
            uuid_snap = get_snapshot_id_from_glance_asyncio(glance_connection, snapshot_name)[0]
        except IndexError:
            uuid_snap = None
        except:
            raise
    return uuid_snap


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
    is_active = False
    while not is_active:
        try:
            is_active = check_availability(nova_connection, snapshot_image_uuid)
        except:
            raise
        if not is_active:
            sleep(2)


@asyncio.coroutine
def make_snapshot_from_uuid_asyncio(nova_connection: NovaConnection, server_uuid: str, snapshot_name: str):
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
    yield from asyncio.ensure_future(check_availability_asyncio(nova_connection, snapshot_image_uuid))


# TODO add a timeout
@asyncio.coroutine
def check_availability_asyncio(nova_connection: NovaConnection, snapshot_image_uuid: str):
    step = {"queued", "saving", "active"}
    print("here")
    image_info = dict(nova_connection.connection.glance.find_image(snapshot_image_uuid).to_dict())
    print("image_info", image_info)
    if 'status' in image_info:
        print(image_info['status'])
        if not image_info['status'] in step:
            raise ValueError("Unknown status : " + image_info['status'])
        if image_info['status'] == "active":
            return True
    return False


def check_availability(nova_connection: NovaConnection, snapshot_image_uuid: str):
    step = {"queued", "saving", "active"}
    print("here")
    image_info = dict(nova_connection.connection.glance.find_image(snapshot_image_uuid).to_dict())
    print("image_info", image_info)
    if 'status' in image_info:
        print(image_info['status'])
        if not image_info['status'] in step:
            raise ValueError("Unknown status : " + image_info['status'])
        if image_info['status'] == "active":
            return True
    return False


def make_volume_snapshot(cinder_connection: CinderConnection, volume_id: str, snapname: str):
    cinder_connection.connection.volume_snapshots.create(volume_id, name=snapname)
