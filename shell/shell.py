import cmd
from json import dumps
from datetime import datetime
from authentication.authentication import AuthenticationV3
from migration.snapshot import make_snapshot
from migration.migration import migration
from migration.launch_instance import launch_instance
from utils.ask_credential import ask_credential
from utils.get_ids import get_ovh_default_nics
from connections.connections import ConnectionsVersion
from connections.connections import Connections


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

    def do_bye(self, arg):
        'Exit the exodus console'
        return True

    def do_exit(self, arg):
        'Exit the exodus console'
        return True

    def do_catalog(self, arg):
        'Print the catalog'
        print(dumps(self._current_connection.catalog, indent=4))

    def do_list_connection(self, arg):
        'List all connection'
        print("Connections: ")
        print('\n'.join(str(connection) for connection in self._connections))

    def do_connection(self, arg):
        'Make a connection'
        print("Connection\n")
        authentication = None
        try:
            authentication = AuthenticationV3() if len(self._connections) == 0 else self._init_auth()
        except:
            authentication = self._init_auth()
        if authentication is not None:
            self._current_connection = Connections(authentication, self._connections_version)
            self._connections.append(self._current_connection)
            print("You are connected to {0} as {1}\n".format(authentication.auth_url, authentication.username))

    def do_change_connection(self, args):
        'Change the current connection into an other.\nUse: change_connection username'
        args = args.split(' ')
        if len(args) == 1:
            connection = self._find_connection(args[0])
            if connection is not None:
                self._current_connection = connection
            else:
                print("The username: " + args[0] + " is not found")
        else:
            print("Bad command")

    def do_migration(self, args):
        'Make a migration between 2 project.\nUse: migration [src_user] src_region [dest_user] dest_region src_instance_name dest_instance_name flavor'
        args = args.split(' ')
        src_user_connection, dest_user_connection = None, None
        src_region, dest_region, src_instance_name, dest_instance_name, flavor = None, None, None, None, None
        if len(args) == 7:
            src_user, src_region, dest_user, dest_region, src_instance_name, dest_instance_name, flavor = map(str, args)
            src_user_connection = self._find_connection(src_user)
            dest_user_connection = self._find_connection(dest_user)
        elif len(args) == 5:
            src_region, dest_region, src_instance_name, dest_instance_name, flavor = map(str, args)
            src_user_connection = self._current_connection
            dest_user_connection = self._current_connection
        if len(args) == 7 or len(args) == 5:
            snapshot_name = str(src_instance_name + str(datetime.now().isoformat()))
            try:
                if src_region in src_user_connection.nova and \
                                src_region in src_user_connection.glance and \
                                dest_region in dest_user_connection.glance and \
                                dest_region in dest_user_connection.nova and \
                                dest_region in dest_user_connection.neutron:
                    print("make snap")
                    make_snapshot(src_user_connection.get_nova_connection(src_region), src_instance_name, snapshot_name)
                    print("snap done")
                    print("make migration")
                    migration(src_user_connection.get_glance_connection(src_region),
                              dest_user_connection.get_glance_connection(dest_region),
                              snapshot_name, snapshot_name, "qcow2", "bare")
                    print("migration done")
                    print("make launch")
                    launch_instance(dest_user_connection.get_nova_connection(dest_region),
                                    dest_instance_name, snapshot_name, flavor,
                                    get_ovh_default_nics(dest_user_connection.get_neutron_connection(dest_region)))
                    print("launch done")
                else:
                    print("Can not find regions in the some connections")
            except Exception as error:
                print(error)
                print("Error")
        else:
            print("Usage error")

    def do_list_flavor(self, args):
        'List all flavor. Can be pass a regions name in parameter'
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
        print("\n".join(str(r) for r in self._current_connection.authentication.global_region))

    def do_list_instance(self, args):
        'List all instance. Can be pass a regions name in parameter'
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
                username = ask_credential([(False, "Username: ")])[0]
                if self._connection_exist(auth_url, username):
                    print("Already login to {0} as {1}".format(auth_url, username))
                    return None
                user_domain_name = ask_credential([(False, "User domain name: ")])[0]
                password = ask_credential([(True, None)])[0]
                authentication = AuthenticationV3(auth_url=auth_url, username=username,
                                                  user_domain_name=user_domain_name, password=password)
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

    def _find_connection(self, username: str):
        """
        Find a connection with username in parameter
        
        :param username: Username of a project 
        :return: None or a connection 
        """
        for connection in self._connections:
            if connection.authentication.username == username:
                return connection
        return None
