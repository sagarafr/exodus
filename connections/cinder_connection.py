from connections.connection import Connection
from cinderclient.client import Client as CinderClient


class CinderConnection(Connection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connection = CinderClient(version=kwargs['version'], session=self.authentication.session, region_name=self.region_name)

    @property
    def region(self):
        return self.authentication.volume_v2_region

    @property
    def endpoints(self):
        return self.authentication.volume_v2
