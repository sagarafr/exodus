from novaclient.client import Client as NovaClient
from authentication.nova_authentication import NovaAuthentication
from authentication.nova_authentication import OVHNovaAuthentication
from .connection import Connection


class NovaConnection(Connection):
    def __init__(self, **kwargs):
        super().__init__()
        self._authentication = NovaAuthentication(**kwargs)

    def connect(self):
        if 'token' in self.authentication:
            del self.authentication['token']
        self.connection = NovaClient(**self.authentication)


class OVHNovaConnection(NovaConnection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._authentication = OVHNovaAuthentication()
