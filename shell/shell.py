import cmd
from json import dumps
from re import search
from re import fullmatch
from math import trunc
from authentication.authentication import *
from utils.ask_credential import ask_credential
from utils.find_flavors import is_good_flavor
from utils.find_flavors import have_instance
from connections.connections import ConnectionsVersion
from connections.connections import Connections
from utils.get_env_variable import get_os_credentials
from migration_task.migration_manager import MigrationManager
from utils.get_ids import get_server_id_from_nova


class Shell(cmd.Cmd):
    """
    A basic exodus shell client. The commands available are :
    * bye / exit : exit the console
    * connection : ask credentials and make a connection to a openstack project
    * change_connection : change the current connection
    * list_connection : list all different connections
    * catalog : print all information of the current connection
    * migration : make a migration of one instance between to 2 regions or 2 projects
    * list_flavor : list flavors of the current connection
    * list_region : list regions of the current connection
    * list_instance : list all instances of the current connection
    """
    intro = "Welcome to the exodus shell. Type help or ? to list commands.\n"
    prompt = '(exodus) '

    def __init__(self):
        super().__init__()
        self._connections_version = ConnectionsVersion()
        self._connections = list()
        self._alias = dict()
        self._current_connection = None
        self._url_validation = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        self._env_connection()

    def do_bye(self, arg):
        'Exit the exodus console'
        return True

    def do_exit(self, arg):
        'Exit the exodus console'
        return True

    def do_catalog(self, arg):
        'Print the catalog'
        if self._current_connection is None:
            print("You must have a valid connection")
        else:
            print(dumps(self._current_connection.catalog, indent=4))

    def do_list_connection(self, arg):
        'List all connection'
        print("Connections: ")
        print('\n'.join(str(connection) for connection in self._connections))

    def do_connection(self, arg):
        'Make a connection'
        print("Connection\n")
        authentication = self._init_auth()
        if authentication is not None:
            self._current_connection = Connections(authentication, self._connections_version)
            self._connections.append(self._current_connection)
            print("You are connected to {0} as {1}\n".format(authentication.auth_url, authentication.username))

    def do_change_connection(self, args):
        'Change the current connection into an other.\nUse: change_connection username'
        args = args.split(' ')
        if len(args) == 1:
            connection = self._find_connection_by_username(args[0])
            if connection is not None:
                self._current_connection = connection
            else:
                connection = self._find_connection_by_token(args[0])
                if connection is None:
                    print("The username or token " + args[0] + " is not found")
        else:
            print("Bad command")

    # TODO make real_migration (make the flavor, dest_instance_name and network optional)
    # TODO delete the old one
    # TODO check the network
    def do_real_migration(self, args):
        'Make a real migration between 2 projects. IN WORKING PROGRESS'
        return

    # TODO add the possibility to choose the network flavor or the id_instance or container_format or disk_format ?
    def do_migration(self, args):
        'Make a migration between 2 project.\nUse: migration [src_user] src_region [dest_user] dest_region src_instance_name dest_instance_name flavor'
        args = [arg.strip() for arg in args.split(' ') if arg != '']
        src_user_connection, dest_user_connection = None, None
        src_region, dest_region, src_instance_name, dest_instance_name, flavor = None, None, None, None, None
        if len(args) == 7:
            src_user, src_region, dest_user, dest_region, src_instance_name, dest_instance_name, flavor = map(str, args)
            src_user_connection = self._find_connection_by_username(src_user)
            dest_user_connection = self._find_connection_by_username(dest_user)
        elif len(args) == 5:
            src_region, dest_region, src_instance_name, dest_instance_name, flavor = map(str, args)
            src_user_connection = self._current_connection
            dest_user_connection = self._current_connection
        if src_user_connection is None:
            print("You don't have a valid connection at source.")
            return
        if dest_user_connection is None:
            print("You don't have a valid connection at destination.")
            return
        if len(args) == 7 or len(args) == 5:
            try:
                if src_region not in src_user_connection.nova:
                    print("{} is not in Nova region module".format(src_region))
                elif dest_region not in dest_user_connection.nova:
                    print("{} is not in Nova region module".format(dest_region))
                elif src_region not in src_user_connection.glance:
                    print("{} is not in Glance region module".format(src_region))
                elif dest_region not in src_user_connection.glance:
                    print("{} is not in Glance region module".format(dest_region))
                elif dest_region not in dest_user_connection.neutron:
                    print("{} is not in Neutron region module".format(dest_region))
                elif not have_instance(src_user_connection.get_nova_connection(src_region), src_instance_name):
                    print("The {0} instance is not in {1} Nova region module".format(src_instance_name, src_region))
                elif not is_good_flavor(src_user_connection.get_nova_connection(src_region), src_instance_name, flavor):
                    print("The flavor {0} is not to small for {1} instance".format(flavor, src_instance_name))
                else:
                    migration_manager = MigrationManager(source_connection=src_user_connection,
                                                         destination_connection=dest_user_connection)
                    server_id = get_server_id_from_nova(src_user_connection.get_nova_connection(src_region), src_instance_name)[0]
                    migration_manager.prepare_migration(server_id, src_region, dest_region)
                    migration_manager.migration()
            except Exception as error:
                print(error)
        else:
            print("Usage error")

    def do_list_flavor(self, args):
        'List all flavor. Can be pass a regions name in parameter'
        if self._current_connection is None:
            print("You must have a connection")
        else:
            if len(args) == 0:
                for region in self._current_connection.nova:
                    print(region)
                    print('\n'.join(str(s) for s in self._current_connection.nova[region].connection.flavors.list()))
            else:
                args = set(args.split(' '))
                for region in args:
                    if region in self._current_connection.nova:
                        print(region)
                        print('\n'.join(str(s) for s in self._current_connection.nova[region].connection.flavors.list()))

    def do_list_region(self, args):
        'List all region'
        if self._current_connection is None:
            print("You must have a connection")
        else:
            print("\n".join(str(r) for r in self._current_connection.authentication.global_region))

    def do_list_instance(self, args):
        'List all instance. Can be pass a regions name in parameter'
        if self._current_connection is None:
            print("You must have a connection")
        else:
            if len(args) == 0:
                for region in self._current_connection.nova:
                    print(region)
                    print('\n'.join(str(s) for s in self._current_connection.nova[region].connection.servers.list()))
            else:
                args = set(args.split(' '))
                for region in args:
                    if region in self._current_connection.nova:
                        print(region)
                        print('\n'.join(str(s) for s in self._current_connection.nova[region].connection.servers.list()))

    def _init_auth(self):
        """
        Initialize a connection. If a connection exist already doesnt create a new connection
        """
        is_auth = False
        authentication = None
        while not is_auth:
            try:
                auth_url = ask_credential([(False, "Auth url: ")])[0]
                if fullmatch(self._url_validation, auth_url) is None:
                    print("Auth url is not a good url")
                    continue

                version = self._get_version(auth_url)
                if version is None or not 2 <= version <= 3:
                    print("Unknown authentication version")
                    continue

                username = ask_credential([(False, "Username: ")])[0]
                if self._connection_exist(auth_url, username):
                    print("Already login to {0} as {1}".format(auth_url, username))
                    return None

                tmp = ask_credential([(False, "User domain name[default by default]: ")])[0]
                user_domain_name = tmp if tmp != '' else "default"

                password = ask_credential([(True, None)])[0]

                authentication = None
                if version == 3:
                    authentication = AuthenticationV3(auth_url=auth_url, username=username,
                                                      user_domain_name=user_domain_name, password=password)
                elif version == 2:
                    tenant_id = ask_credential([(False, "Tenant id: ")])[0]
                    authentication = AuthenticationV2(auth_url=auth_url, username=username,
                                                      password=password, tenant_id=tenant_id)
            except TypeError as type_error:
                print(type_error)
                continue
            except Exception as exception_error:
                print(exception_error)
                print("Connection failed. Try again")
                continue
            is_auth = True
        return authentication

    def _connection_exist(self, auth_url: str, username: str):
        """
        Check if a connection exists already

        :param auth_url: Authentication url with version 3 
        :param username: Username of the project
        """
        for connection in self._connections:
            if connection.authentication.auth_url == auth_url and connection.authentication.username == username:
                return True
        return False

    def _find_connection_by_username(self, username: str):
        """
        Find a connection with username in parameter
        
        :param username: Username of a project 
        :return: None or a connection 
        """
        for connection in self._connections:
            if connection.authentication.username == username:
                return connection
        return None

    def _find_connection_by_token(self, token: str):
        """
        Find a connection with token in parameter

        :param token: Token of a project 
        :return: None or a connection 
        """
        for connection in self._connections:
            if connection.authentication.token == token:
                return connection
        return None

    @staticmethod
    def _get_version(auth_url: str):
        """
        Get the version number from an url
        :param auth_url: string url
        :return: int version number
        """
        search_group = search(".*/v([0-9.]+).*", auth_url)
        if search_group is None or search_group.groups == 0:
            version = ask_credential([False, "Version of Auth url: "])[0]
        else:
            version = search_group.group(1)
        if version is not None:
            try:
                version = int(trunc(float(version)))
            except ValueError:
                return None
        return version

    def _env_connection(self):
        """
        Make an environment connection
        """
        auth_url, token, username, password, user_domain_name, tenant_id = get_os_credentials()
        auth = None

        if auth_url is None and (token is None and (username is None or password is None)):
            return None

        try:
            auth = AuthenticationV3(auth_url=auth_url, token=token)
            self._add_connection(auth)
            self._print_auth_token(auth)
        except Exception as exception_message:
            print(exception_message)
            pass
        if auth is None:
            try:
                auth = AuthenticationV3(auth_url=auth_url, username=username,
                                        password=password, user_domain_name=user_domain_name)
                self._add_connection(auth)
                self._print_auth_url(auth)
            except Exception as exception_message:
                print(exception_message)
                pass

        if auth is None:
            try:
                auth = AuthenticationV2(auth_url=auth_url, token=token, tenant_id=tenant_id)
                self._add_connection(auth)
                self._print_auth_token(auth)
            except Exception as exception_message:
                print(exception_message)
                pass
        if auth is None:
            try:
                auth = AuthenticationV2(auth_url=auth_url, username=username, password=password, tenant_id=tenant_id)
                self._add_connection(auth)
                self._print_auth_url(auth)
            except Exception as exception_message:
                print(exception_message)
                pass

    @staticmethod
    def _print_auth_url(auth: Authentication):
        if auth is not None:
            print("You are connected to {} as {}\n".format(auth.auth_url, auth.username))

    @staticmethod
    def _print_auth_token(auth: Authentication):
        if auth is not None:
            print("You are connected to {} with a token\n".format(auth.auth_url))

    def _add_connection(self, auth):
        if auth is not None:
            try:
                self._current_connection = Connections(auth, self._connections_version)
                self._connections.append(self._current_connection)
            except Exception:
                raise
