from connections.glance_connection import GlanceConnection
from utils.get_ids import get_snapshot_id_from_glance
from tempfile import NamedTemporaryFile
from os import mkfifo
from os import fork
from os import unlink
from os import wait
from os import _exit as exit_child


# TODO make this more secure again and maybe disk_format and container_format optional
# TODO make an other function that take directly the uuid of the snapshot ?
def migration(glance_source: GlanceConnection, glance_destination: GlanceConnection,
              snapshot_name: str, server_name_dest: str,
              disk_format: str, container_format: str):
    """
    Launch the migration of a snapshot_name between 2 GlanceConnection regions in "streaming" mode
    If there are multiple 

    :param glance_source: GlanceConnection object source
    :param glance_destination: GlanceConnection object destination
    :param snapshot_name: str content the snapshot in region of glance_source and put in the glance_destination region
    :param server_name_dest: str content the snapshot name in the glance_destionation region
    :param disk_format: str content the disk_format of the snapshot
    :param container_format: str content the container_format of the snapshot
    """
    snapshot_uuid_list = get_snapshot_id_from_glance(glance_source, snapshot_name)
    if len(snapshot_uuid_list) == 0:
        raise ValueError("Couldn't find the following snapshot: " + snapshot_name)

    # TODO lets make a user choice or raise an exception ?
    snapshot_uuid = snapshot_uuid_list[0]
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
