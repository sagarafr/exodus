from openstack import connection as os_connection
from authentication.openstack_authentication import OVHOpenStackAuthentication
from authentication.openstack_authentication import OpenStackAuthentication
from .connection import Connection


class OpenStackConnection(Connection):
    def __init__(self, **kwargs):
        super().__init__()
        self._authentication = OpenStackAuthentication(**kwargs)

    @property
    def authenticator(self):
        return self.connection.authenticator

    @property
    def session(self):
        return self.connection.session

    @property
    def token(self):
        return self.session.get_token(self.authenticator)

    def connect(self):
        self.connection = os_connection.Connection(**self.authentication)


class OVHOpenStackConnection(OpenStackConnection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._authentication = OVHOpenStackAuthentication()
