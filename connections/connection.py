from authentication.authentication import AuthenticationV3


class Connection(dict):
    """
    Connection interface that take a dict
    Useful to make a connection or pass an existing connection to one module to an other
    """
    def __init__(self, **kwargs):
        """
        Inheritance with dict
        :param kwargs: * 'authentication_v3' content an AuthenticationV3 object
        * 'auth_url' / 'username' / 'password' / 'user_domain_name' that make an AuthenticationV3 object 
        """
        super().__init__(kwargs)
        if 'authentication_v3' not in self:
            self._authentication = AuthenticationV3(self.auth_url, self.username, self.password, self.user_domain_name)
        else:
            self._authentication = self['authentication_v3']
        self._connection = None

    @property
    def auth_url(self):
        """
        Auth url property content in the dict

        :return: str content the auth url property 
        """
        return self['auth_url']

    @property
    def username(self):
        """
        Username property content in the dict

        :return: str content username property 
        """
        return self['username']

    @property
    def password(self):
        """
        Password property content in the dict

        :return: str content password property 
        """
        return self['password']

    @property
    def user_domain_name(self):
        """
        User domain name property content in the dict

        :return: str content user_domain_name 
        """
        return self['user_domain_name']

    @property
    def authentication_v3(self):
        """
        AuthenticationV3 property content in the dict
        
        :return: AuthenticationV3 object
        """
        return self['authentication_v3']

    @property
    def authentication(self):
        """
        Authentication property content in the class

        :return: AuthenticationV3 object 
        """
        return self._authentication

    @property
    def connection(self):
        """
        Connection property content in the class

        :return: None or a connection
        """
        return self._connection

    @authentication.setter
    def authentication(self, value):
        """
        Authentication setter property

        :param value: AuthenticationV3 object 
        """
        self._authentication = value

    @property
    def region(self):
        """
        Global region property content in the AuthenticationV3 class

        :return: set or None content all region in the module 
        """
        return self.authentication.global_region

    @property
    def url(self):
        """
        Url content in endpoint of module

        :return: set content url in str
        """
        return set(element['url'] for element in self.endpoints if 'url' in element)

    @property
    def endpoints(self):
        """
        Endpoints property
        :raise: NotImplemented because of its depend of connection module
        """
        raise NotImplemented("Endpoints is not implemented in Connection class")

    def __str__(self):
        return "{auth_url:{0},username:{1},user_domain_name:{2}".format(self.auth_url, self.username, self.user_domain_name)