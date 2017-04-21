from glanceclient import Client as GlanceClient

from authentication.authentication import Authentication
from connections.connection import Connection


class GlanceConnection(Connection):
    def __init__(self, **kwargs):
        super().__init__()
        self._authentication = Authentication(**kwargs)

    def connect(self):
        self.connection = GlanceClient(version=self.authentication['version'],
                                       endpoint=self.authentication['endpoint'],
                                       token=self.authentication['token'])

    @property
    def authentication(self):
        return self._authentication

    @property
    def region_name(self):
        return self.authentication['region']

    @property
    def token(self):
        return self.authentication.token

    @token.setter
    def token(self, value):
        self.authentication.token = value

    @region_name.setter
    def region_name(self, region_name):
        self.authentication['region'] = region_name
        self.authentication['endpoint'] = "https://image.compute." + self.region_name.lower() + ".cloud.ovh.net/"


class OVHGlanceConnection(GlanceConnection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.authentication['version'] = '2'
        if 'region' not in kwargs:
            self.region_name = "SBG3"
        self.authentication['endpoint'] = "https://image.compute." + self.region_name.lower() + ".cloud.ovh.net/"
