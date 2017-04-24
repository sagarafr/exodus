from neutronclient.v2_0.client import Client as NeutronClient
from authentication.neutron_authentication import NeutronAuthentication
from authentication.neutron_authentication import OVHNeutronAuthentication
from connections.connection import Connection


class NeutronConnection(Connection):
    def __init__(self, **kwargs):
        super().__init__()
        self._authentication = NeutronAuthentication(**kwargs)

    def connect(self):
        self.connection = NeutronClient(**self._authentication)

    @property
    def region_name(self):
        return self._authentication['region_name']

    @region_name.setter
    def region_name(self, value):
        self._authentication['region_name'] = value


class OVHNeutronConnection(NeutronConnection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._authentication = OVHNeutronAuthentication()
