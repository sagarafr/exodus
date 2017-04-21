from authentication.authentication import Authentication
from authentication.authentication import OVHAuthentication


class NeutronAuthentication(Authentication):
    def __init__(self, **kwargs):
        self["region_name"] = ""
        super().__init__(**kwargs)

    @property
    def region_name(self):
        return self["region_name"]

    @region_name.setter
    def region_name(self, value):
        self["region_name"] = value


class OVHNeutronAuthentication(NeutronAuthentication, OVHAuthentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["version"] = "2.0"
        self["auth_url"] = "https://auth.cloud.ovh.net/v2.0"
        del self["token"]
        if self.region_name == "":
            self.region_name = "SBG3"

    @property
    def version(self):
        return self["version"]

    @version.setter
    def version(self, value: str):
        self["version"] = value
