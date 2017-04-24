from authentication.authentication import Authentication


class Connection(object):
    def __init__(self):
        super().__init__()
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

    def import_credentials(self, authentication: Authentication):
        self.authentication.import_authentication(authentication)

    def ask_credentials(self):
        self.authentication.ask_credentials()
