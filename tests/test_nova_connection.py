from connections.nova_connection import OVHNovaConnection


def main():
    ovh_nova_connection = OVHNovaConnection()
    ovh_nova_connection.ask_credentials()
    ovh_nova_connection.region_name = "BHS3"
    ovh_nova_connection.connect()
    for server in ovh_nova_connection.connection.servers.list():
        print(server)


if __name__ == '__main__':
    main()
