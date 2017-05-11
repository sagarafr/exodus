from keystoneauth1.identity import v3
from keystoneauth1.identity import v2
from keystoneauth1.identity.v2 import Auth
from keystoneauth1.session import Session
from os import environ


class Authentication(object):
    """
    Basic Authentication method to make basic session
    """
    def __init__(self, auth_url: str = None, username: str = None, password: str = None, user_domain_name: str = None, tenant_id: str = None):
        """
        Authentication method. This check the environment but take priority from arguments

        :param auth_url: str Authentication url 
        :param username: str Username
        :param password: str Password
        :param user_domain_name: str User domain name (Not exist in version 2 but important for version 3)
        :param tenant_id: str Tenant id (Important for version 2 but can be drop)
        """
        self._authentication = None
        self._tenant_id = None
        self._session = None
        self._access = None
        self._catalog = None

        try:
            auth_url = auth_url if auth_url is not None else environ['OS_AUTH_URL']
            username = username if username is not None else environ['OS_USERNAME']
            password = password if password is not None else environ['OS_PASSWORD']
            user_domain_name = user_domain_name if user_domain_name is not None else environ['OS_USER_DOMAIN_NAME']
        except KeyError as key_error:
            raise ValueError("{} not found or not initialize".format(key_error))

        self.connection(auth_url, username, password, user_domain_name, tenant_id)

    def connection(self, auth_url: str = "", username: str = "", password: str = "", user_domain_name: str = "default", tenant_id: str = ""):
        """
        Make a connection.

        :param auth_url: str Authentication url 
        :param username: str Username
        :param password: str Password
        :param user_domain_name: str User domain name (Not exist in version 2 but important for version 3)
        :param tenant_id: str Tenant id (Important for version 2 but can be drop)
        :raise: NotImplementedError 
        """
        raise NotImplementedError("connection method must be implemented")

    @property
    def authentication(self):
        """
        Authentication property

        :return: v3.Password object
        """
        return self._authentication

    @property
    def token(self):
        """
        Token property

        :return: Token string
        """
        return self.session.get_token(self.authentication)

    @authentication.setter
    def authentication(self, value: Auth):
        """
        Authentication setter

        :param value: v3.Password 
        """
        self._authentication = value

    @property
    def session(self):
        """
        Session property

        :return: Session object 
        """
        return self._session

    @session.setter
    def session(self, value: Session):
        """
        Session setter

        :param value: Session object 
        """
        self._session = value

    @property
    def access(self):
        """
        AccessInfo property

        :return: AccessInfo object
        """
        return self._access

    @property
    def catalog(self):
        """
        Catalog property

        :return: dict content the catalog of connection 
        """
        return self._catalog

    @property
    def volume(self):
        """
        Endpoint of the volume property

        :return: None or dict content endpoints
        """
        return self._get_endpoint("volume")

    @property
    def volume_region(self):
        """
        Region of the volume property

        :return:  None or set content all region property
        """
        return self._get_region(self.volume)

    @property
    def identity(self):
        """
        Endpoint of the identity property

        :return: None or dict content endpoints
        """
        return self._get_endpoint("identity")

    @property
    def identity_region(self):
        """
        Region of the identity property

        :return: None or set content all region property 
        """
        return self._get_region(self.identity)

    @property
    def compute(self):
        """
        Endpoint of the compute property

        :return: None or dict content endpoints
        """
        return self._get_endpoint("compute")

    @property
    def compute_region(self):
        """
        Region of the compute property

        :return: None or set content all region property
        """
        return self._get_region(self.compute)

    @property
    def network(self):
        """
        Endpoint of the network property

        :return: None or dict content endpoints 
        """
        return self._get_endpoint("network")

    @property
    def network_region(self):
        """
        Region of the network property

        :return: None or set content all region property
        """
        return self._get_region(self.network)

    @property
    def image(self):
        """
        Endpoint of the image property

        :return: None or dict content endpoints 
        """
        return self._get_endpoint("image")

    @property
    def image_region(self):
        """
        Region of the image property

        :return: None or set content all region property
        """
        return self._get_region(self.image)

    @property
    def object_store(self):
        """
        Endpoint of the object store property

        :return: None or dict content endpoints 
        """
        return self._get_endpoint("object-store")

    @property
    def object_store_region(self):
        """
        Region of the object store property

        :return: None or set content all region property
        """
        return self._get_region(self.object_store)

    @property
    def volume_v2(self):
        """
        Endpoint of the volume 2 property

        :return: None or dict content endpoints 
        """
        return self._get_endpoint("volumev2")

    @property
    def volume_v2_region(self):
        """
        Region of the volume 2 property

        :return: None or set contentn all region property 
        """
        return self._get_region(self.volume_v2)

    @property
    def auth_url(self):
        """
        Authentication url property

        :return: str content the url authentication 
        """
        return self.authentication.auth_url

    @property
    def username(self):
        """
        Username property

        :return: str content the username 
        :raise: NotImplementedError if call from Authentication class
        """
        raise NotImplementedError("Must implement username")

    @property
    def password(self):
        """
        Password property

        :return: str content the password
        :raise: NotImplementedError if call from Authentication class
        """
        raise NotImplementedError("Must implement password")

    @property
    def user_domain_id(self):
        """
        User domain name property

        :return: str content the user domain name
        :raise: NotImplementedError if call from Authentication class
        """
        raise NotImplementedError("Must implement user domain id")

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def global_region(self):
        """
        Region in common of all identity, compute, network, image, object_store and volume_v2 module

        :return: set content all region in str
        """
        global_regions = self._get_region(self.volume)
        global_regions.intersection(self._get_region(self.identity))
        global_regions.intersection(self._get_region(self.compute))
        global_regions.intersection(self._get_region(self.network))
        global_regions.intersection(self._get_region(self.image))
        global_regions.intersection(self._get_region(self.object_store))
        global_regions.intersection(self._get_region(self.volume_v2))
        return global_regions

    def _get_endpoint(self, type_name: str):
        """
        Get endpoint method

        :param type_name: module type
        :return: None or dict content all endpoints of type_name module
        """
        for element in self.catalog:
            element = dict(element)
            if "type" in element and "endpoints" in element and element["type"] == type_name:
                return element["endpoints"]
        return None

    @staticmethod
    def _get_region(elements: dict = None):
        """
        Get region method

        :param elements: elements content all information in a module 
        :return: None or set content all region
        """
        raise NotImplementedError("Must implement _get_region function")

    def __str__(self):
        return "Auth url: " + str(self.auth_url) + " | Username: " + str(self.username)


class AuthenticationV3(Authentication):
    """
    Basic Authentication method to make a basic session V3
    """
    def __init__(self, auth_url: str = None, username: str = None, password: str = None, user_domain_name: str = "default", tenant_id: str = None):
        """
        Authentication method. This check the environment but take priority from arguments

        :param auth_url: str Authentication url 
        :param username: str Username
        :param password: str Password
        :param user_domain_name: str User domain name (Not exist in version 2 but important for version 3)
        :param tenant_id: str Tenant id (Important for version 2 but can be drop)
        """
        super().__init__(auth_url, username, password, user_domain_name, tenant_id)

    def connection(self, auth_url: str = "", username: str = "", password: str = "", user_domain_name: str = "default", tenant_id: str = ""):
        """
        Make a connection.

        :param auth_url: str Authentication url 
        :param username: str Username
        :param password: str Password
        :param user_domain_name: str User domain name (Not exist in version 2 but important for version 3)
        :param tenant_id: str Tenant id (Important for version 2 but can be drop)
        """
        self._authentication = v3.Password(auth_url=auth_url, username=username,
                                           password=password, user_domain_name=user_domain_name)
        self._session = Session(auth=self.authentication)
        self._access = self.authentication.get_access(session=self.session)
        self._catalog = None if not self.access.has_service_catalog() else self.access.__dict__['_data']['token']['catalog']

    @property
    def username(self):
        return self.authentication.get_cache_id_elements()['password_username']

    @property
    def password(self):
        return self.authentication.get_cache_id_elements()['password_password']

    @property
    def user_domain_id(self):
        return self.authentication.get_cache_id_elements()['password_user_domain_name']

    @staticmethod
    def _get_region(elements: dict = None):
        return set(
            element['region_id'] for element in elements if 'region_id' in element) if elements is not None else None


class AuthenticationV2(Authentication):
    """
    Basic Authentication method to make a basic session V2
    """
    def __init__(self, auth_url: str = "", username: str = "", password: str = "", user_domain_name: str = "default", tenant_id: str = None):
        """
        Authentication method. This check the environment but take priority from arguments

        :param auth_url: str Authentication url 
        :param username: str Username
        :param password: str Password
        :param user_domain_name: str User domain name (Not exist in version 2 but important for version 3)
        :param tenant_id: str Tenant id (Important for version 2 but can be drop)
        """
        super().__init__(auth_url, username, password, user_domain_name, tenant_id)

    def connection(self, auth_url: str = "", username: str = "", password: str = "", user_domain_name: str = "default0", tenant_id: str = ""):
        """
        Make a connection.

        :param auth_url: str Authentication url 
        :param username: str Username
        :param password: str Password
        :param user_domain_name: str User domain name (Not exist in version 2 but important for version 3)
        :param tenant_id: str Tenant id (Important for version 2 but can be drop)
        :raise: ValueError if OS_TENANT_ID is not defined
        """
        try:
            tenant_id = tenant_id if tenant_id is not None else environ['OS_TENANT_ID']
        except KeyError as key_error:
            raise ValueError("{} not found or not initialize".format(key_error))

        self._authentication = v2.Password(auth_url=auth_url, username=username, password=password, tenant_id=tenant_id)
        self._session = Session(auth=self.authentication)
        self._tenant_id = tenant_id
        self._access = self.authentication.get_access(session=self.session)
        self._catalog = None if not self.access.has_service_catalog() else self.access.__dict__['_data']['access']['serviceCatalog']

    @property
    def username(self):
        return self.authentication.get_cache_id_elements()['username']

    @property
    def password(self):
        return self.authentication.get_cache_id_elements()['password']

    @property
    def user_domain_id(self):
        return self.authentication.get_cache_id_elements()['auth_url']

    @staticmethod
    def _get_region(elements: dict = None):
        return set(
            element['region'] for element in elements if 'region' in element) if elements is not None else None
