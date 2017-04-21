from authentication.authentication import Authentication
from authentication.authentication import OVHAuthentication


class NovaAuthentication(Authentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class OVHNovaAuthentication(NovaAuthentication, OVHAuthentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["version"] = "2"

    @property
    def version(self):
        return self["version"]

    @version.setter
    def version(self, value: str):
        self["version"] = value
