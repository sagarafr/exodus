from connections.nova_connection import NovaConnection
from getpass import getpass
from json import dumps
from utils.find_flavors import is_good_flavor
from copy import deepcopy


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "region_name": "BHS3",
             "version": "2"}
    creds_gra = deepcopy(creds)
    creds_gra['region_name'] = "GRA3"
    ovh_nova_connection = NovaConnection(**creds)
    ovh_nova_connection_gra = NovaConnection(**creds_gra)

    for server in ovh_nova_connection.connection.servers.list():
        print(server)
        server_info = dict(server.to_dict())
        print(server_info)

        for interface in ovh_nova_connection.connection.servers.interface_list(server_info['id']):
            print(interface.to_dict())

    for server in ovh_nova_connection_gra.connection.servers.list():
        print(server)
        server_info = dict(server.to_dict())
        print(server_info)

        for interface in ovh_nova_connection.connection.servers.interface_list(server_info['id']):
            print(interface.to_dict())

"""
    for flavor in ovh_nova_connection.connection.flavors.list():
        flavor_info = dict(flavor.to_dict())
        print(dumps(flavor_info))

    print(is_good_flavor(ovh_nova_connection, input("Instance name: "), input("Flavor name: ")))
"""

if __name__ == '__main__':
    main()
