from authentication.authentication import AuthenticationV3
from authentication.authentication import AuthenticationV2
from connections.glance_connection import GlanceConnection
from getpass import getpass


def test_auth_v3():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass()}
    connection = AuthenticationV3(**creds)
    glance_creds = {"region_name": "GRA3",
                    "version": "2",
                    "authentication": connection}
    ovh_glance_connection = GlanceConnection(**glance_creds)
    for image in ovh_glance_connection.connection.images.list():
        print(image)
    print()

    glance_creds = {"region_name": "BHS3",
                    "version": "2",
                    "authentication": connection}
    ovh_glance_connection = GlanceConnection(**glance_creds)
    for image in ovh_glance_connection.connection.images.list():
        print(image)


def test_auth_v2():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v2.0",
             "tenant_id": input("Tenant id: "),
             "username": input("Username: "),
             "password": getpass()}
    connection = AuthenticationV2(**creds)
    glance_creds = {"region_name": "GRA3",
                    "version": "2",
                    "authentication": connection}
    ovh_glance_connection = GlanceConnection(**glance_creds)
    for image in ovh_glance_connection.connection.images.list():
        print(image)
    print()


def tesst_auth_v4(connection):
    glance_creds = {"region_name": "BHS3",
                    "version": "2",
                    "authentication": connection}
    ovh_glance_connection = GlanceConnection(**glance_creds)
    for image in ovh_glance_connection.connection.images.list():
        print(image)
        print(image.__dict__)


def main():
    test_auth_v2()

if __name__ == '__main__':
    main()
