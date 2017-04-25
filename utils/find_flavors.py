from connections.nova_connection import NovaConnectionV3


def find_flavors_v3(nova_connection: NovaConnectionV3, flavor_name: str):
    flavor_list = []
    for flavor in nova_connection.connection.flavors.list():
        flavor_info = dict(flavor.to_dict())
        if 'name' in flavor_info and 'id' in flavor_info and flavor_info['name'] == flavor_name:
            flavor_list.append(flavor_info['id'])
    return flavor_list
