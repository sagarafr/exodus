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
                                      region_name=self['region_name'])

    @property
    def endpoints(self):
        """
        Endpoints property of compute AuthenticationV3

        :return: None or dict content endpoints
        """
        return self.authentication.compute

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

    def __str__(self):
        return super().__str__() + '}' if 'region_name' not in self else "region_name:{0}".format(self.region_name)
