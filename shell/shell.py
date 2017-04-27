from authentication.authentication import AuthenticationV3
from connections.glance_connection import GlanceConectionV3
from connections.neutron_connection import NeutronConnectionV3
from connections.nova_connection import NovaConnectionV3
from migration.snapshot import make_snapshot_v3
from migration.migration import migration_v3
from migration.launch_instance import launch_instance_v3
from utils.ask_credential import ask_credential
from utils.get_ids import get_ovh_default_nics_v3
from json import dumps
from datetime import datetime
import cmd


class ConnectionsVersion:
    def __init__(self):
        self._glance_version = "2"
        self._neutron_version = "2"
        self._nova_version = "2"

    @property
    def nova_version(self):
        return self._nova_version

    @property
    def neutron_version(self):
        return self._neutron_version

    @property
    def glance_version(self):
        return self._glance_version


class Connections:
    def __init__(self, authentication: AuthenticationV3, connections_versions: ConnectionsVersion):
        self._authentication = authentication
        self._connection_version = connections_versions
        self._glance_connections = dict()
        self._neutron_connections = dict()
        self._nova_connections = dict()
        self._init_connections()

    @property
    def authentication(self):
        return self._authentication

    @property
    def glance(self):
        return self._glance_connections

    @property
    def neutron(self):
        return self._neutron_connections

    @property
    def nova(self):
        return self._nova_connections

    def get_glance_connection(self, region):
        return self.glance[region]

    def get_nova_connection(self, region):
        return self.nova[region]

    def get_neutron_connection(self, region):
        return self.neutron[region]

    def _init_connection(self, regions, version, init_function, var_storage):
        for region in regions:
            credentials = {"region_name": str(region),
                           "version": str(version),
                           "authentication_v3": self.authentication}
            var_storage[str(region)] = init_function(**credentials)

    def _init_connections(self):
        self._init_connection(self.authentication.image_region, self._connection_version.glance_version,
                              GlanceConectionV3, self._glance_connections)
        self._init_connection(self.authentication.network_region, self._connection_version.neutron_version,
                              NeutronConnectionV3, self._neutron_connections)
        self._init_connection(self.authentication.compute_region, self._connection_version.nova_version,
                              NovaConnectionV3, self._nova_connections)

    def __str__(self):
        return str(self._authentication)


class Shell(cmd.Cmd):
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

    def do_migration(self, args):
        'Make a migration between 2 project.\n\
        Use: migration_between_project [src_user] src_region [dest_user] dest_region src_instance_name \
        dest_instance_name flavor'
        args = args.split(' ')
        print(len(args))
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
                    make_snapshot_v3(src_user_connection.get_nova_connection(src_region), src_instance_name, snapshot_name)
                    print("snap done")
                    print("make migration")
                    migration_v3(src_user_connection.get_glance_connection(src_region),
                                 dest_user_connection.get_glance_connection(dest_region),
                                 snapshot_name, snapshot_name, "qcow2", "bare")
                    print("migration done")
                    print("make launch")
                    launch_instance_v3(dest_user_connection.get_nova_connection(dest_region),
                                       dest_instance_name, snapshot_name, flavor,
                                       get_ovh_default_nics_v3(dest_user_connection.get_neutron_connection(dest_region)))
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
        for connection in self._connections:
            if connection.authentication.auth_url == auth_url and connection.authentication.username == username:
                return True
        return False

    def _find_connection(self, username: str):
        for connection in self._connections:
            if connection.authentication.username == username:
                return connection
        return None
