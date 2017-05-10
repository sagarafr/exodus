from authentication.authentication import Authentication
from authentication.authentication import AuthenticationV2
from authentication.authentication import AuthenticationV3


class Connection(dict):
    """
    Connection interface that take a dict
    Useful to make a connection or pass an existing connection to one module to an other
    """
    def __init__(self, **kwargs):
        """
        Inheritance with dict
        :param kwargs: * 'authentication' content an Authentication object
        * 'auth_url' / 'username' / 'password' / 'user_domain_name' that make an AuthenticationV3 object
        * 'auth_url' / 'username' / 'password' / 'tenant_id' that make an AuthenticationV3 object
        """
        super().__init__(kwargs)
        if 'authentication' not in self:
            if 'tenant_id' in self:
                self._authentication = AuthenticationV2(auth_url=self.auth_url, username=self.username,
                                                        password=self.password, tenant_id=self.tenant_id)
            else:
                self._authentication = AuthenticationV3(auth_url=self.auth_url, username=self.username,
                                                        password=self.password, user_domain_name=self.user_domain_name)
        else:
            self._authentication = self['authentication']
        self._connection = None

    @property
    def auth_url(self):
        """
        Auth url property content in the dict

        :return: str content the auth url property 
        """
        return self['auth_url'] if 'auth_url' in self else None

    @property
    def username(self):
        """
        Username property content in the dict

        :return: str content username property 
        """
        return self['username'] if 'username' in self else None

    @property
    def password(self):
        """
        Password property content in the dict

        :return: str content password property 
        """
        return self['password'] if 'password' in self else None

    @property
    def user_domain_name(self):
        """
        User domain name property content in the dict

        :return: str content user_domain_name property
        """
        return self['user_domain_name'] if 'user_domain_name' in self else None

    @property
    def tenant_id(self):
        """
        Tenant id property int the dict

        :return: str content tenant_id property
        """
        return self['tenant_id'] if 'tenant_id' in self else None

    @property
    def authentication_content(self):
        """
        Authentication property content in the dict
        
        :return: Authentication object
        """
        return self['authentication']

    @property
    def authentication(self):
        """
        Authentication property content in the class

        :return: Authentication object
        """
        return self._authentication

    @property
    def connection(self):
        """
        Connection property content in the class

        :return: None or a connection
        """
        return self._connection

    @property
    def region_name(self):
        """
        Region name property

        :return: str content the region name
        """
        return self['region_name'] if 'region_name' in self else None

    @region_name.setter
    def region_name(self, value):
        """
        Change only the property of region_name. DO NOT MAKE A RECONNECTION AFTER THIS

        :param value: str content the region name in glance module
        """
        self['region_name'] = value

    @authentication.setter
    def authentication(self, value: Authentication):
        """
        Authentication setter property

        :param value: Authentication object
        """
        self._authentication = value

    @property
    def region(self):
        """
        Global region property content in the Authentication class

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
        Endpoints property of Authentication

        :raise: NotImplemented because of its depend of connection module
        """
        raise NotImplemented("Endpoints is not implemented in Connection class")

    def __str__(self):
        return "{auth_url:{0},username:{1},user_domain_name:{2}".format(self.auth_url, self.username, self.user_domain_name)
