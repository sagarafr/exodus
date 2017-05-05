from neutronclient.v2_0.client import Client as NeutronClient
from connections.connection import Connection


class NeutronConnection(Connection):
    """
    NeutronConnection module that contain a NeutronClient connection
    """
    def __init__(self, **kwargs):
        """
        :param kwargs: *region_name = region name of NeutronClient
        """
        super().__init__(**kwargs)
        self._connection = NeutronClient(session=self.authentication.session, region_name=self.region_name)

    @property
    def region_name(self):
        """
        Region name property
        :return: str content the region name
        """
        return self['region_name']

    @region_name.setter
    def region_name(self, value):
        """
        Change only the property of region_name. DO NOT MAKE A RECONNECTION AFTER THIS

        :param value: str content the region name in glance module
        """
        self['region_name'] = value

    @property
    def region(self):
        """
        Region property of network_region AuthenticationV3

        :return: None or set content all region property 
        """
        return self.authentication.network_region
