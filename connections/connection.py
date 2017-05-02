from authentication.authentication import AuthenticationV3


class Connection(dict):
    """
    kwars = dict
    auth_url, username, password, user_domain_name, authentication_v3
    """
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        if 'authentication_v3' not in self:
            self._authentication = AuthenticationV3(self.auth_url, self.username, self.password, self.user_domain_name)
        else:
            self._authentication = self['authentication_v3']
        self._connection = None

    @property
    def auth_url(self):
        return self['auth_url']

    @property
    def username(self):
        return self['username']

    @property
    def password(self):
        return self['password']

    @property
    def user_domain_name(self):
        return self['user_domain_name']

    @property
    def authentication_v3(self):
        return self['authentication_v3']

    @property
    def authentication(self):
        return self._authentication

    @property
    def connection(self):
        return self._connection

    @authentication.setter
    def authentication(self, value):
        self._authentication = value

    @property
    def region(self):
        return self.authentication.global_region

    @property
    def url(self):
        return set(element['url'] for element in self.endpoints if 'url' in element)

    @property
    def endpoints(self):
        raise NotImplemented("Endpoints is not implemented in Connection class")

    def __str__(self):
        return "{auth_url:{0},username:{1},user_domain_name:{2}".format(self.auth_url, self.username, self.user_domain_name)