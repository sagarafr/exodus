from connections.glance_connection import GlanceConnection
from connections.neutron_connection import NeutronConnection
from connections.nova_connection import NovaConnection
from authentication.authentication import AuthenticationV3


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
                              GlanceConnection, self._glance_connections)
        self._init_connection(self.authentication.network_region, self._connection_version.neutron_version,
                              NeutronConnection, self._neutron_connections)
        self._init_connection(self.authentication.compute_region, self._connection_version.nova_version,
                              NovaConnection, self._nova_connections)

    def __str__(self):
        return str(self._authentication)
