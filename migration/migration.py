from connections.glance_connection import GlanceConnection
from utils.get_ids import get_snapshot_id_from_glance
from tempfile import NamedTemporaryFile
from os import mkfifo
from os import fork
from os import unlink
from os import wait
from os import _exit as exit_child


def migration(glance_source: GlanceConnection, glance_destination: GlanceConnection,
              snapshot_name: str, server_name_dest: str,
              disk_format: str = "qcow2", container_format: str = "bare"):
    """
    Launch the migration of a snapshot_name between 2 GlanceConnection regions in "streaming" mode
    If there are multiple 

    :param glance_source: GlanceConnection object source
    :param glance_destination: GlanceConnection object destination
    :param snapshot_name: str content the snapshot in region of glance_source and put in the glance_destination region
    :param server_name_dest: str content the snapshot name in the glance_destionation region
    :param disk_format: str content the disk_format of the snapshot
    :param container_format: str content the container_format of the snapshot
    :raise: ValueError if snapshot_name is not found
    """
    snapshot_uuid = None
    try:
        snapshot_uuid = get_snapshot_id_from_glance(glance_source, snapshot_name)[0]
    except IndexError as index:
        raise ValueError(snapshot_name + " snapshot not found")
    try:
        migration_from_uuid(glance_source, glance_destination, snapshot_uuid, server_name_dest,
                            disk_format, container_format)
    except:
        raise


def migration_from_uuid(glance_source: GlanceConnection, glance_destination: GlanceConnection,
                        snapshot_uuid, server_name_dest: str,
                        disk_format: str = "qcow2", container_format: str = "bare"):
    data = glance_source.connection.images.data(snapshot_uuid)
    pipe_filename = NamedTemporaryFile().name
    image = glance_destination.connection.images.create(name=server_name_dest,
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
