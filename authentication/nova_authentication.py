from authentication.authentication import Authentication
from authentication.authentication import OVHAuthentication


class NovaAuthentication(Authentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class OVHNovaAuthentication(NovaAuthentication, OVHAuthentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["version"] = "2"
        if 'region_name' not in self:
            self['region_name'] = "SBG3"

    @property
    def version(self):
        return self["version"]

    @version.setter
    def version(self, value: str):
        self["version"] = value

    @property
    def region_name(self):
        return self['region_name']

    @region_name.setter
    def region_name(self, value):
        self['region_name'] = value
