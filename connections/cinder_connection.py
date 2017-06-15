from connections.connection import Connection
from cinderclient.client import Client as CinderClient


class CinderConnection(Connection):
    """
    CinderConnection module that contain a CinderClient connection
    """
    def __init__(self, **kwargs):
        """
        :param version: version of CinderClient
        :param region_name: region name of CinderClient
        """
        super().__init__(**kwargs)
        self._connection = CinderClient(version=kwargs['version'], session=self.authentication.session, region_name=self.region_name)

    @property
    def region(self):
        """
        Region property of volume_v2 Authentication
        
        :return: None or set content all region property 
        """
        return self.authentication.volume_v2_region

    @property
    def endpoints(self):
        """
        Endpoints property of image Authentication
        
        :return: None or dict content endpoints 
        """
        return self.authentication.volume_v2
