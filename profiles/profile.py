from openstack import profile


class Profile(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_regions(self, regions: set):
        for region in regions:
            self.add_region(region)

    def add_region(self, region: str):
        self[region] = profile.Profile()
        self[region].set_region(profile.Profile.ALL, region)


class OVHProfile(Profile):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_regions({"SBG3", "GRA3", "BHS3"})

    @property
    def sbg(self):
        return self["SBG3"]

    @property
    def gra(self):
        return self["GRA3"]

    @property
    def bhs(self):
        return self["BHS3"]

    def get_profile(self, value):
        return self[value]
