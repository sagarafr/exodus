from connections.nova_connection import NovaConnectionV3
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "region_name": "SBG3",
             "version": "2"}
    ovh_nova_connection = NovaConnectionV3(**creds)
    print(ovh_nova_connection.endpoints)
    for server in ovh_nova_connection.connection.servers.list():
        print(server)


if __name__ == '__main__':
    main()
