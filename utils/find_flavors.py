from connections.nova_connection import NovaConnection


def find_flavors(nova_connection: NovaConnection, flavor_name: str):
    """
    Find all flavor_name from nova_connection

    :param nova_connection: NovaConnection 
    :param flavor_name: str flavor to find
    :return: list of flavors id
    """
    flavor_list = []
    for flavor in nova_connection.connection.flavors.list():
        flavor_info = dict(flavor.to_dict())
        if 'name' in flavor_info and 'id' in flavor_info and flavor_info['name'] == flavor_name:
            flavor_list.append(flavor_info['id'])
    return flavor_list


def find_flavor_name(nova_connection: NovaConnection, flavor_id: str):
    """
    Find all flavor name from nova_connection with the id flavor_id

    :param nova_connection: NovaConnection
    :param flavor_id: str flavor id to find
    :return: list of flavors name 
    """
    flavor_list = []
    for flavor in nova_connection.connection.flavors.list():
        flavor_info = dict(flavor.to_dict())
        if 'id' in flavor_info and 'name' in flavor_info and flavor_info['id'] == flavor_id:
            flavor_list.append(flavor_info['name'])
    return flavor_list


def have_instance(nova_connection: NovaConnection, instance_name: str):
    """
    Check if the instance_name is in the same region that nova_connection

    :param nova_connection: NovaConnection 
    :param instance_name: str content the instance name
    :return: bool
    """
    for server in nova_connection.connection.servers.list():
        server_info = dict(server.to_dict())
        if 'name' in server_info and server_info['name'] == instance_name:
            return True
    return False


def is_good_flavor(nova_connection: NovaConnection, instance_src_name: str, flavor_dest: str):
    """
    Return True if the disk capacity of flavor_dest is superior or equal to the disk capacity of instance_src_name instance
    
    :param nova_connection: NovaConnection in the same region of instance_src_name
    :param instance_src_name: Instance to compare
    :param flavor_dest: Flavor to compare
    :return: True or False
    """
    server_flavor_list = []
    base_disk = None
    server_disk_list = []
    for server in nova_connection.connection.servers.list():
        server_info = dict(server.to_dict())
        if 'name' in server_info and 'flavor' in server_info and 'id' in server_info['flavor'] and server_info['name'] == instance_src_name:
            server_flavor_list.append(server_info['flavor']['id'])

    for flavor in nova_connection.connection.flavors.list():
        flavor_info = dict(flavor.to_dict())
        if 'name' in flavor_info and 'disk' in flavor_info and flavor_dest == flavor_info['name']:
            base_disk = int(flavor_info['disk'])
        if 'id' in flavor_info and 'disk' in flavor_info and flavor_info['id'] in server_flavor_list:
            server_disk_list.append(int(flavor_info['disk']))
    if base_disk is None or len(server_disk_list) == 0:
        return False

    for server_disk in server_disk_list:
        if server_disk > base_disk:
            return False
    return True


def find_flavor_name_from_id(nova_connection: NovaConnection, flavor_id: str):
    """
    Find the name of the flavor with the id flavor_id in the same region that nova_connection

    :param nova_connection: NovaConnection 
    :param flavor_id: str content the id of the flavor
    :return: str content the name of the flavor or None 
    """
    try:
        flavor_info = nova_connection.connection.flavors.get(flavor_id)
    except Exception:
        return None
    flavor_info = dict(flavor_info.to_dict())
    if 'name' in flavor_info:
        return flavor_info['name']
    return None
