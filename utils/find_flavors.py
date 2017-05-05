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
