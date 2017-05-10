from connections.nova_connection import NovaConnection


def find_flavors(nova_connection: NovaConnection, flavor_name: str):
    """
    Find all flavor_name from nova_connection

    :param nova_connection: NovaConnection 
    :param flavor_name: flavor to find
    :return: list of flavors
    """
    flavor_list = []
    for flavor in nova_connection.connection.flavors.list():
        flavor_info = dict(flavor.to_dict())
        if 'name' in flavor_info and 'id' in flavor_info and flavor_info['name'] == flavor_name:
            flavor_list.append(flavor_info['id'])
    return flavor_list


def have_instance(nova_connection: NovaConnection, instance_name: str):
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
