from connections.glance_connection import GlanceConnection
from authentication.authentication import AuthenticationV3
from migration.migration import migration
from getpass import getpass


def main():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass()}
    connection = AuthenticationV3(**creds)
    glance_creds_src = {"region_name": input("Region name at source: "),
                        "version": "2",
                        "authentication_v3": connection}
    glance_creds_dest = {"region_name": input("Region name at destination: "),
                         "version": "2",
                         "authentication_v3": connection}

    ovh_glance_connection_source = GlanceConnection(**glance_creds_src)
    ovh_glance_connection_destination = GlanceConnection(**glance_creds_dest)
    migration(ovh_glance_connection_source, ovh_glance_connection_destination,
              input("Snapshot name at source: "), input("Snapshot name at destination: "))


if __name__ == '__main__':
    main()
