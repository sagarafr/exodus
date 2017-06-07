from connections.glance_connection import GlanceConnection


def get_disk_format(glance_connection: GlanceConnection, snapshot_name: str):
    """
    Get a list of disk format of snapshot_name from glance_connection region
    
    :param glance_connection: GlanceConnection to get the region
    :param snapshot_name: str to get the snapshot_name
    :return: lsit of str corresponding of disk format of snapshot
    """
    disk_format_list = []
    for image in glance_connection.connection.images.list():
        image_info = dict(image)
        if 'disk_format' in image_info and 'name' in image_info and image_info['name'] == snapshot_name:
            disk_format_list.append(str(image_info['disk_format']))
    return disk_format_list


def get_container_format(glance_connection: GlanceConnection, snapshot_name: str):
    """
    Get a list of container format of snapshot_name from glance_connection region
    
    :param glance_connection: GlanceConnection to get the region
    :param snapshot_name: str to get the snapshot_name
    :return: list of str corresponding of container format of snapshot
    """
    container_format_list = []
    for image in glance_connection.connection.images.list():
        image_info = dict(image)
        if 'container_format' in image_info and 'name' in image_info and image_info['name'] == snapshot_name:
            container_format_list.append(str(image_info['container_format']))
    return container_format_list


def get_instance_type_name(glance_connection: GlanceConnection, instance_name: str):
    """
    Get all the instance type name with instance_name instance name from glance_connection region 

    :param glance_connection: GlanceConnection
    :param instance_name: str content the name of the instance
    :return: list of the instance_type_name
    """
    instance_name_list = []
    for image in glance_connection.connection.images.list():
        image_info = dict(image)
        if 'instance_type_name' in image_info and 'name' in image_info and image_info['name'] == instance_name:
            instance_name_list.append(str(image_info['instance_type_name']))
    return instance_name_list
