from openstack import connection as os_connection
from authentication.openstack_authentication import OVHOpenStackAuthentication
from authentication.openstack_authentication import OpenStackAuthentication
from profiles.profile import OVHProfile
from connections.connection import Connection


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

    def credentials_to_dict(self):
        credentials = dict(self.authentication)
        credentials['token'] = self.token
        return credentials


class OVHOpenStackConnection(OpenStackConnection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ovh_profile = OVHProfile()
        self._authentication = OVHOpenStackAuthentication()

    @property
    def profile(self):
        return self._authentication.profile

    @profile.setter
    def profile(self, value):
        self._authentication.profile = self._ovh_profile.get_profile(value)
        self._authentication["region_name"] = value
