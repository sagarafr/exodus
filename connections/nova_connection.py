from novaclient.client import Client as NovaClient
from connections.connection import Connection


class NovaConnection(Connection):
    """
    NeutronConnection module that contain a NovaClient connection
    """
    def __init__(self, **kwargs):
        """
        :param kwargs: *version = version of NovaClient
        * region_name of NovaClient
        """
        super().__init__(**kwargs)
        self._connection = NovaClient(session=self.authentication.session, version=self['version'],
                                      region_name=self.region_name)

    @property
    def region(self):
        """
        Region property of compute_region Authentication 

        :return: None or set content all region property
        """
        return self.authentication.compute_region

    @property
    def endpoints(self):
        """
        Endpoints property of compute Authentication

        :return: None or dict content endpoints
        """
        return self.authentication.compute

    def __str__(self):
        return super().__str__() + '}' if 'region_name' not in self else "region_name:{0}".format(self.region_name)
