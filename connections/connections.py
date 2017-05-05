import configparser
from connections.glance_connection import GlanceConnection
from connections.neutron_connection import NeutronConnection
from connections.nova_connection import NovaConnection
from authentication.authentication import AuthenticationV3


class ConnectionsVersion:
    """
    ConnectionVersion class content all version hard coded in module
    """
    def __init__(self, filename: str = ""):
        """
        Change the initialization in function of module version
        """
        config = self._init_configuration(filename)
        self._glance_version = config.get("Glance", "version") if config is not None and config.has_section("Glance") and config.has_option("Glance", "version") else "2"
        self._neutron_version = config.get("Neutron", "version") if config is not None and config.has_section("Neutron") and config.has_option("Nova", "version") else "2"
        self._nova_version = config.get("Nova", "version") if config is not None and config.has_section("Nova") and config.has_option("Nova", "version") else "2"

    @property
    def nova_version(self):
        """
        Nova version

        :return: str of nova version
        """
        return self._nova_version

    @property
    def neutron_version(self):
        """
        Neutron version

        :return: str of neutron version
        """
        return self._neutron_version

    @property
    def glance_version(self):
        """
        Glance version

        :return: str of glance version 
        """
        return self._glance_version

    @staticmethod
    def _init_configuration(configure_file):
        config = configparser.ConfigParser()
        try:
            with open(configure_file, 'r') as fd_file:
                config.read_file(fd_file)
        except FileNotFoundError as file_not_found:
            return None
        except PermissionError as permissions:
            return None
        except Exception as exception:
            return None
        return config


class Connections:
    """
    Connections manager that manage all glance, neutron and nova connections in all regions
    """
    def __init__(self, authentication: AuthenticationV3, connections_versions: ConnectionsVersion):
        """
        :param authentication: AuthenticationV3 object 
        :param connections_versions: ConnectionsVersion object
        """
        self._authentication = authentication
        self._connection_version = connections_versions
        self._glance_connections = dict()
        self._neutron_connections = dict()
        self._nova_connections = dict()
        self._init_connections()

    @property
    def authentication(self):
        """
        AuthenticationV3 property

        :return: AuthenticationV3 object 
        """
        return self._authentication

    @property
    def glance(self):
        """
        Glance property

        :return: dict content all glance connections in function of region name key
        """
        return self._glance_connections

    @property
    def neutron(self):
        """
        Neutron property

        :return: dict content all neutron connections in function of region name key
        """
        return self._neutron_connections

    @property
    def nova(self):
        """
        Nova property

        :return: dict content all nova connections in function of region name key
        """
        return self._nova_connections

    def get_glance_connection(self, region):
        """
        Get glance connection in function of region given
        
        :param region: region name of the glance connection
        :return: GlanceConnection object
        """
        return self.glance[region]

    def get_nova_connection(self, region):
        """
        Get nova connection in function of region given

        :param region: region name of the nova connection 
        :return: NovaConnection object
        """
        return self.nova[region]

    def get_neutron_connection(self, region):
        """
        Get neutron connection in function of region given

        :param region: region name of the neutron connection 
        :return: NeutronConnection object
        """
        return self.neutron[region]

    def _init_connection(self, regions, version, init_function, var_storage):
        """
        Initialise in var_storage with init_function in function of regions and version connection

        :param regions: set content all region of type connection
        :param version: str content version of the connection
        :param init_function: function that can initialize a connection
        :param var_storage: dict that can contain all connections
        """
        for region in regions:
            credentials = {"region_name": str(region),
                           "version": str(version),
                           "authentication_v3": self.authentication}
            var_storage[str(region)] = init_function(**credentials)

    def _init_connections(self):
        """
        Initialize all image, network and compute_region connections between all regions
        """
        self._init_connection(self.authentication.image_region, self._connection_version.glance_version,
                              GlanceConnection, self._glance_connections)
        self._init_connection(self.authentication.network_region, self._connection_version.neutron_version,
                              NeutronConnection, self._neutron_connections)
        self._init_connection(self.authentication.compute_region, self._connection_version.nova_version,
                              NovaConnection, self._nova_connections)

    def __str__(self):
        return str(self._authentication)