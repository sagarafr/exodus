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
    def region(self):
        """
        Region property of network_region Authentication

        :return: None or set content all region property
        """
        return self.authentication.network_region

    @property
    def endpoints(self):
        """
        Endpoints property of network Authentication

        :return: None or dict content endpoints
        """
        return self.authentication.network
