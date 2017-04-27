from connections.glance_connection import GlanceConectionV3
from utils.get_ids import get_snapshot_id_from_glance_v3
from tempfile import NamedTemporaryFile
from os import mkfifo
from os import fork
from os import unlink
from os import wait


def migration_v3(glance_source: GlanceConectionV3, glance_destination: GlanceConectionV3,
                 snapshot_name: str, server_name_dest: str,
                 disk_format: str, container_format: str):
    snapshot_uuid_list = get_snapshot_id_from_glance_v3(glance_source, snapshot_name)
    if len(snapshot_uuid_list) == 0:
        raise ValueError("Couldn't find the following snapshot: " + snapshot_name)

    # TODO lets make a user choice
    snapshot_uuid = snapshot_uuid_list[0]
    data = glance_source.connection.images.data(snapshot_uuid)
    pipe_filename = NamedTemporaryFile().name
    image = glance_destination.connection.images.create(name=server_name_dest,
                                                        disk_format=disk_format,
                                                        container_format=container_format)
    image_uuid = str(image.get('id'))

    if data.wrapped is not None:
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
            exit(0)
