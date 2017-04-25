from glanceclient import Client as GlanceClient
from connections.connection import ConnectionV3


class GlanceConectionV3(ConnectionV3):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connection = GlanceClient(version=kwargs['version'], session=self.authentication.session)

    @property
    def endpoints(self):
        return self.authentication.image

    @property
    def region(self):
        return self.authentication.image_region

    @property
    def region_name(self):
        return self['region']

    @region_name.setter
    def region_name(self, value):
        self['region'] = value
