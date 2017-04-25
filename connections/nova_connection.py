from novaclient.client import Client as NovaClient
from connections.connection import ConnectionV3


class NovaConnectionV3(ConnectionV3):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connection = NovaClient(session=self.authentication.session, version=self['version'],
                                      region_name=self['region_name'])

    @property
    def endpoints(self):
        return self.authentication.compute

    @property
    def region_name(self):
        return self['region_name']

    @region_name.setter
    def region_name(self, value):
        self['region_name'] = value
