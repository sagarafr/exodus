from connections.glance_connection import GlanceConnection


def get_disk_format(glance_connection: GlanceConnection, snapshot_name: str):
    disk_format_list = []
    for image in glance_connection.connection.images.list():
        image_info = dict(image)
        if 'disk_format' in image_info and 'name' in image_info and image_info['name'] == snapshot_name:
            disk_format_list.append(image_info['disk_format'])
    return disk_format_list


def get_container_format(glance_connection: GlanceConnection, snapshot_name: str):
    container_format_list = []
    for image in glance_connection.connection.images.list():
        image_info = dict(image)
        if 'container_format' in image_info and 'name' in image_info and image_info['name'] == snapshot_name:
            container_format_list.append(image_info['container_format'])
    return container_format_list
