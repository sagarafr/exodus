from keystoneauth1.identity import v3
from keystoneauth1.session import Session
from os import environ


class AuthenticationV3:
    def __init__(self, auth_url: str = "", username: str = "", password: str = "", user_domain_name: str = "default"):
        auth_url = auth_url if auth_url != "" else environ['OS_AUTH_URL']
        username = username if username != "" else environ['OS_USERNAME']
        password = password if password != "" else environ['OS_PASSWORD']
        user_domain_name = user_domain_name if user_domain_name != "" else environ['OS_USER_DOMAIN_NAME']
        self._authentication = v3.Password(auth_url=auth_url, username=username,
                                           password=password, user_domain_name=user_domain_name)
        self._session = Session(auth=self.authentication)
        self._access = self.authentication.get_access(session=self.session)
        self._catalog = None if not self.access.has_service_catalog() else self.access.__dict__['_data']['token']['catalog']

    @property
    def authentication(self):
        return self._authentication

    @property
    def token(self):
        return self.session.get_token(self.authentication)

    @authentication.setter
    def authentication(self, value: v3.Password):
        self._authentication = value

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    @property
    def access(self):
        return self._access

    @property
    def catalog(self):
        return self._catalog

    @property
    def volume(self):
        return self._get_endpoint("volume")

    @property
    def volume_region(self):
        return self._get_region(self.volume)

    @property
    def identity(self):
        return self._get_endpoint("identity")

    @property
    def identity_region(self):
        return self._get_region(self.identity)

    @property
    def compute(self):
        return self._get_endpoint("compute")

    @property
    def compute_region(self):
        return self._get_region(self.compute)

    @property
    def network(self):
        return self._get_endpoint("network")

    @property
    def network_region(self):
        return self._get_region(self.network)

    @property
    def image(self):
        return self._get_endpoint("image")

    @property
    def image_region(self):
        return self._get_region(self.image)

    @property
    def object_store(self):
        return self._get_endpoint("object-store")

    @property
    def object_store_region(self):
        return self._get_region(self.object_store)

    @property
    def volume_v2(self):
        return self._get_endpoint("volumev2")

    @property
    def auth_url(self):
        return self.authentication.auth_url

    @property
    def username(self):
        return self.authentication.get_cache_id_elements()['password_username']

    @property
    def password(self):
        return self.authentication.get_cache_id_elements()["password_password"]

    @property
    def user_domain_id(self):
        return self.authentication.get_cache_id_elements()["password_user_domain_name"]

    @property
    def global_region(self):
        global_regions = self._get_region(self.volume)
        global_regions.intersection(self._get_region(self.identity))
        global_regions.intersection(self._get_region(self.compute))
        global_regions.intersection(self._get_region(self.network))
        global_regions.intersection(self._get_region(self.image))
        global_regions.intersection(self._get_region(self.object_store))
        global_regions.intersection(self._get_region(self.volume_v2))
        return global_regions

    def _get_endpoint(self, type_name: str):
        for element in self.catalog:
            element = dict(element)
            if "type" in element and "endpoints" in element and element["type"] == type_name:
                return element["endpoints"]
        return None

    @staticmethod
    def _get_region(elements: dict = None):
        return set(element['region_id']for element in elements if 'region_id' in element) if elements is not None else None

    def __str__(self):
        return "Auth url: " + str(self.auth_url) + " | Username: " + str(self.username)
