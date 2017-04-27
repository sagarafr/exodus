from neutronclient.v2_0.client import Client as NeutronClient
from connections.connection import Connection


class NeutronConnection(Connection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connection = NeutronClient(session=self.authentication.session, region_name=self.region_name)

    @property
    def region_name(self):
        return self['region_name']

    @region_name.setter
    def region_name(self, value):
        self['region_name'] = value

    @property
    def region(self):
        return self.authentication.network_region
