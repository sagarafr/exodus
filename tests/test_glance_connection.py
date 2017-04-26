from authentication.authentication import AuthenticationV3
from connections.glance_connection import GlanceConectionV3
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass()}
    connection = AuthenticationV3(**creds)
    glance_creds = {"region_name": "GRA3",
                    "version": "2",
                    "authentication_v3": connection}
    ovh_glance_connection = GlanceConectionV3(**glance_creds)
    for image in ovh_glance_connection.connection.images.list():
        print(image)
    print()

    glance_creds = {"region_name": "BHS3",
                    "version": "2",
                    "authentication_v3": connection}
    ovh_glance_connection = GlanceConectionV3(**glance_creds)
    for image in ovh_glance_connection.connection.images.list():
        print(image)


if __name__ == '__main__':
    main()
