from connections.neutron_connection import NeutronConnection
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "region_name": "BHS3",
             "version": "2"}
    ovh_neutron_connection = NeutronConnection(**creds)
    print(ovh_neutron_connection.connection.list_networks())


if __name__ == '__main__':
    main()
