import cmd
from json import dumps
from re import search
from re import fullmatch
from math import trunc
from authentication.authentication import *
from utils.ask_credential import ask_credential
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
        # TODO make here a dict to store connection with 2 keys: token and password
        self._connections = {"token": [], "password": []}
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
        if len(self._connections["token"]) == 0 and len(self._connections["password"]) == 0:
            print("Have no current connection")
        else:
            if len(self._connections["token"]) != 0:
                print("Token connections: ")
                connections = self._connections["token"]
                print('\n'.join([str(index_connection + 1) + ': ' + str(connections[index_connection]) for index_connection in range(0, len(connections))]))
            if len(self._connections["password"]) != 0:
                print("Password connections: ")
                connections = self._connections["password"]
                print('\n'.join([str(index_connection + 1) + ': ' + str(connections[index_connection]) for index_connection in range(0, len(connections))]))

    def do_connection(self, arg):
        'Make a connection'
        print("Connection")
        authentication, method = self._init_auth()
        if authentication is not None and method is not None:
            self._add_connection(authentication, method)
            print(authentication)

    def do_change_connection(self, args):
        'Change the current connection into an other.\nUse: change_connection url username or url token'
        args = self._cleaning_args(args)
        if len(args) == 2:
            url, data = args
            connections = self._find_connection(url, data)
            if len(connections) == 0:
                print("Don't find the url and username or url and token data")
            elif len(connections) == 1:
                self._current_connection = connections[0]
                print("Current connection changed")
            else:
                index_connection = self._choose_connection_in_list(connections)
                self._current_connection = connections[index_connection]
                print("Current connection changed")
        else:
            print("Bad command")

    def do_migration(self, args):
        'Make a migration between 2 project.\nUse: migration [auth_url src_user or auth_url src_token] src_region [auth_url dest_user or auth_url dest_token] dest_region instance_name or instance_id'
        args = self._cleaning_args(args)
        src_user_connection, dest_user_connection = None, None
        src_region, dest_region, src_instance_name = None, None, None
        if len(args) == 7:
            auth_url_src, src_user, src_region, auth_url_dest, dest_user, dest_region, src_instance_name = map(str, args)
            src_user_connection = self._find_connection(auth_url_src, src_user)
            dest_user_connection = self._find_connection(auth_url_dest, dest_user)
        elif len(args) == 3:
            src_region, dest_region, src_instance_name = map(str, args)
            src_user_connection = self._current_connection
            dest_user_connection = self._current_connection
        else:
            print("Usage error")
            return

        if src_user_connection is None:
            print("You don't have a valid connection at source.")
            return
        if dest_user_connection is None:
            print("You don't have a valid connection at destination.")
            return

        if len(args) == 7 or len(args) == 3:
            try:
                if type(src_user_connection) is list:
                    if len(src_user_connection) == 0:
                        print("You don't have a valid connection at source.")
                        return
                    elif len(src_user_connection) == 1:
                        src_user_connection = src_user_connection[0]
                    else:
                        src_user_connection = src_user_connection[self._choose_connection_in_list(src_user_connection)]
                if type(dest_user_connection) is list:
                    if len(dest_user_connection) == 0:
                        print("You don't have a valid connection at destination.")
                        return
                    elif len(dest_user_connection) == 1:
                        dest_user_connection = dest_user_connection[0]
                    else:
                        dest_user_connection = dest_user_connection[self._choose_connection_in_list(dest_user_connection)]

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
                else:
                    migration_manager = MigrationManager(source_connection=src_user_connection,
                                                         destination_connection=dest_user_connection)
                    try:
                        server_id = get_server_id_from_nova(src_user_connection.get_nova_connection(src_region), src_instance_name)[0]
                    except:
                        server_id = src_instance_name
                    migration_manager.prepare_migration(server_id, src_region, dest_region)
                    migration_manager.migration()
            except Exception as error:
                print(error)

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
        authentication = None
        connection_method = self._ask_connection_method()
        if connection_method == "token":
            authentication = self._init_auth_token()
        elif connection_method == "password":
            authentication = self._init_auth_password()
        return authentication, connection_method

    def _init_auth_token(self):
        authentication = None
        while authentication is None:
            try:
                auth_url = ask_credential([(False, "Auth url: ")])[0]
                if fullmatch(self._url_validation, auth_url) is None:
                    print("Auth url is not a good url")
                    continue

                version = self._get_version(auth_url)
                if version is None or not 2 <= version <= 3:
                    print("Unknown authentication version")
                    continue

                token = ask_credential([(False, "Token: ")])[0]
                if self._connection_exist(auth_url, token):
                    print("Already token to {0} as {1}".format(auth_url, token))
                    return None

                tenant_id = None
                if version == 2:
                    tenant_id = ask_credential([(False, "Tenant id: ")])[0]
                authentication, method = self._try_to_make_an_authentication(auth_url=auth_url, token=token, tenant_id=tenant_id, print_error=True)

            except TypeError as type_error:
                print(type_error)
                continue
            except Exception as exception_error:
                print(exception_error)
                continue
        return authentication

    def _init_auth_password(self):
        authentication = None
        while authentication is None:
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
                tenant_id = None

                if version == 2:
                    tenant_id = ask_credential([(False, "Tenant id: ")])[0]
                authentication, method = self._try_to_make_an_authentication(auth_url=auth_url, username=username,
                                                                             user_domain_name=user_domain_name, password=password,
                                                                             tenant_id=tenant_id, print_error=True)

            except TypeError as type_error:
                print(type_error)
                continue
            except Exception as exception_error:
                print(exception_error)
                continue
        return authentication

    def _connection_exist(self, auth_url: str, data: str):
        """
        Check if a connection exists already

        :param auth_url: Authentication url with version 3 
        :param data: Username of the project
        """
        return len(self._find_connection(auth_url, data)) != 0

    def _find_connection(self, auth_url: str, data: str):
        connection = self._find_connection_by_username(auth_url, data)
        if len(connection) == 0:
            connection = self._find_connection_by_token(auth_url, data)
        return connection

    def _find_connection_by_username(self, auth_url: str, username: str):
        """
        Find a connection with username in parameter
        
        :param username: Username of a project 
        :return: None or a connection 
        """
        list_connection = []
        for connection in self._connections['password']:
            if connection.authentication.username == username and connection.authentication.auth_url == auth_url:
                list_connection.append(connection)
        return list_connection

    def _find_connection_by_token(self, auth_url: str, token: str):
        """
        Find a connection with token in parameter

        :param token: Token of a project 
        :return: None or a connection 
        """
        list_connection = []
        for connection in self._connections['token']:
            if connection.authentication.token == token and connection.authentication.auth_url == auth_url:
                list_connection.append(connection)
        return list_connection

    def _env_connection(self):
        """
        Make an environment connection
        """
        auth_url, token, username, password, user_domain_name, tenant_id = get_os_credentials()

        if auth_url is None and (token is None and (username is None or password is None)):
            return None

        auth, method = self._try_to_make_an_authentication(auth_url, token, username, password, user_domain_name, tenant_id)
        if auth is not None and method is not None:
            self._add_connection(auth, method)
            print("Connected with {}".format(auth))

    def _add_connection(self, auth: Authentication, method: str):
        if auth is not None and method is not None:
            try:
                self._current_connection = Connections(auth, self._connections_version)
                self._connections[method].append(self._current_connection)
            except Exception:
                raise

    @staticmethod
    def _try_to_make_an_authentication(auth_url: str, token: str = None, username: str = None, password: str = None, user_domain_name: str = None, tenant_id: str = None, print_error: bool = False):
        method, auth = None, None
        try:
            auth = AuthenticationV3(auth_url=auth_url, token=token)
            method = "token"
        except Exception as exception_message:
            if print_error:
                print("Authentication version 3 with token failed : {}".format(exception_message))
            pass
        if auth is None:
            try:
                auth = AuthenticationV3(auth_url=auth_url, username=username,
                                        password=password, user_domain_name=user_domain_name)
                method = "password"
            except Exception as exception_message:
                if print_error:
                    print("Authentication version 3 with password failed : {}".format(exception_message))
                pass

        if auth is None:
            try:
                auth = AuthenticationV2(auth_url=auth_url, token=token, tenant_id=tenant_id)
                method = "token"
            except Exception as exception_message:
                if print_error:
                    print("Authentication version 2 with token failed : {}".format(exception_message))
                pass
        if auth is None:
            try:
                auth = AuthenticationV2(auth_url=auth_url, username=username, password=password, tenant_id=tenant_id)
                method = "password"
            except Exception as exception_message:
                if print_error:
                    print("Authentication version 2 with password failed : {}".format(exception_message))
                pass
        return auth, method

    @staticmethod
    def _cleaning_args(args):
        r_args = []
        is_escaping = False
        arg = ""
        for c in args:

            if not is_escaping and c == '\\':
                is_escaping = True
                continue

            if is_escaping:
                arg += c
                is_escaping = False
                continue

            if c == ' ':
                if arg != "":
                    r_args.append(arg)
                    arg = ""
                    continue
            else:
                arg += c
        if arg != "":
            r_args.append(arg)
        return r_args

    @staticmethod
    def _extract_auth_url_and_data(arg):
        args_split = arg.split(':')
        if len(args_split) != 2:
            return None, None
        return args_split[0], args_split[1]

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

    @staticmethod
    def _ask_connection_method():
        method = None
        while method is None:
            try:
                method = ask_credential([(False, "Which method between token and password [token by default]: ")])[0]
                if method == "":
                    method = "token"
                else:
                    if method != "token" and method != "password":
                        method = None
            except TypeError as type_error:
                print(type_error)
            except Exception as exception_error:
                print(exception_error)
        return method

    @staticmethod
    def _choose_connection_in_list(connection_list: list):
        print("You have multiple connection")
        index_connection = None
        while index_connection is None:
            print("Take one connection in this list: ")
            print('\n'.join(
                [str(index_connection + 1) + ': ' + str(connection_list[index_connection]) for index_connection in range(0, len(connection_list))]))
            try:
                index_connection = int(ask_credential([(False, "Index: ")])[0])
            except Exception as exception_message:
                print(exception_message)
            if index_connection not in range(0, len(connection_list)):
                index_connection = None
        return index_connection
