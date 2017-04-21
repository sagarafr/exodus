from connections.openstack_project import OpenStackProject


class Connection(object):
    def __init__(self):
        self._authentication = None
        self._connection = None

    @property
    def authentication(self):
        return self._authentication

    @authentication.setter
    def authentication(self, value):
        self._authentication = value

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value

    def connect(self):
        raise NotImplemented("Must implement connect function")

    def import_credentials(self, credentials: OpenStackProject):
        self.authentication.import_authentication_from_project(credentials)

    def ask_credentials(self):
        self.authentication.ask_credentials()
