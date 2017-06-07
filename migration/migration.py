from connections.glance_connection import GlanceConnection
from utils.get_ids import get_snapshot_id_from_glance
from tempfile import NamedTemporaryFile
from os import mkfifo
from os import fork
from os import unlink
from os import wait
from os import _exit as exit_child


def migration(glance_source: GlanceConnection, glance_destination: GlanceConnection, snapshot_name_source: str,
              snapshot_name_destination: str, disk_format: str = "qcow2", container_format: str = "bare"):
    """
    Launch the migration of a snapshot_name between 2 GlanceConnection regions in "streaming" mode
    If there are multiple the first one is taken

    :param glance_source: GlanceConnection object source
    :param glance_destination: GlanceConnection object destination
    :param snapshot_name_source: str content the snapshot name to transfer
    :param snapshot_name_destination: str content the snapshot name in the glance_destination region
    :param disk_format: str content the disk_format of the snapshot
    :param container_format: str content the container_format of the snapshot
    :raise: ValueError if snapshot_name_source is not found
    """
    try:
        snapshot_uuid = get_snapshot_id_from_glance(glance_source, snapshot_name_source)[0]
    except IndexError:
        raise ValueError(snapshot_name_source + " snapshot not found")
    try:
        migration_from_uuid(glance_source, glance_destination, snapshot_uuid, snapshot_name_destination, disk_format,
                            container_format)
    except:
        raise


def migration_from_uuid(glance_source: GlanceConnection, glance_destination: GlanceConnection, snapshot_uuid: str,
                        snapshot_name_destination: str, disk_format: str = "qcow2", container_format: str = "bare"):
    """
    Launch the migration of a snapshot_uuid between 2 GlanceConnection regions in "streaming" mode

    :param glance_source: GlanceConnection object source
    :param glance_destination: GlanceConnection object destination
    :param snapshot_uuid: str content the uuid of the snapshot to transfer
    :param snapshot_name_destination: str content the 
    :param disk_format: str content the disk_format of the snapshot
    :param container_format: str content the container_format of the snapshot
    """
    data = glance_source.connection.images.data(snapshot_uuid)
    pipe_filename = NamedTemporaryFile().name
    image = glance_destination.connection.images.create(name=snapshot_name_destination,
                                                        disk_format=disk_format,
                                                        container_format=container_format)
    image_uuid = str(image.get('id'))

    if data.wrapped is not None:
        # TODO test this with a read buffer
        # TODO test make multi read and multi write
        mkfifo(pipe_filename)
        if fork() != 0:
            reading_pipe = open(pipe_filename, 'rb')
            glance_destination.connection.images.upload(image_uuid, reading_pipe)
            reading_pipe.close()
            unlink(pipe_filename)
            wait()
        else:
            writing_pipe = open(pipe_filename, 'wb')
            for binary_data in data.wrapped:
                writing_pipe.write(binary_data)
            writing_pipe.close()
            exit_child(0)
