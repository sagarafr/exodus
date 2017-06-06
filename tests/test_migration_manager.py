from migration_task.migration_manager import MigrationManager
from authentication.authentication import AuthenticationV3
from connections.connections import Connections
from connections.connections import ConnectionsVersion
import traceback
import logging
from getpass import getpass


def main():
    auth = AuthenticationV3(auth_url=input("Auth url: "), username=input("Username: "),
                            password=getpass(), user_domain_name='default')
    connections = Connections(authentication=auth, connections_versions=ConnectionsVersion())
    migration_manager = MigrationManager(source_connection=connections, destination_connection=connections)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    try:
        migration_manager.prepare_migration(instance_id=input("Instance id: "),
                                            region_name_source=input("Region name source: "),
                                            region_name_destination=input("Region name destination: "))
        print(migration_manager.resource_manager)
    except Exception as exception_message:
        print(exception_message)
        traceback.print_stack()


if __name__ == '__main__':
    main()
