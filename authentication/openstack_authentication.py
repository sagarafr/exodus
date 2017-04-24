from authentication.authentication import Authentication
from authentication.authentication import OVHAuthentication


class OpenStackAuthentication(Authentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class OVHOpenStackAuthentication(OVHAuthentication, OpenStackAuthentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["profile"] = None

    @property
    def profile(self):
        return self["profile"]

    @profile.setter
    def profile(self, value):
        self["profile"] = value
