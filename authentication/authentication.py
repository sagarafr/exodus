from connections.openstack_project import OpenStackProject


class Authentication(dict):
    def __init__(self, **kwargs):
        self["project_id"] = ""
        self["username"] = ""
        self["password"] = ""
        self["token"] = ""
        super().__init__(**kwargs)

    @property
    def project_id(self):
        return self["project_id"]

    @project_id.setter
    def project_id(self, value):
        self["project_id"] = value

    @property
    def username(self):
        return self["username"]

    @username.setter
    def username(self, value):
        self["username"] = value

    @property
    def password(self):
        return self["password"]

    @password.setter
    def password(self, value):
        self["password"] = value

    @property
    def token(self):
        return self["token"]

    @token.setter
    def token(self, value):
        self["token"] = value

    @property
    def authentication(self):
        return self.project_id, self.username, self.password, self.token

    @authentication.setter
    def authentication(self, value):
        self.project_id, self.username, self.password, self.token = value

    def import_authentication_from_project(self, openstack_project: OpenStackProject):
        self.authentication = (openstack_project.project_id, openstack_project.user_id,
                               openstack_project.password, openstack_project.token)

    def ask_credentials(self):
        credentials = OpenStackProject()
        credentials.ask_credentials()
        self.import_authentication_from_project(credentials)

    def credentials_to_dict(self):
        return dict([('project_id', self.project_id), ('username', self.username), ('password', self.password)])


class OVHAuthentication(Authentication):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["user_domain_name"] = "default"
        self["auth_url"] = "https://auth.cloud.ovh.net/v3"

    @property
    def user_domain_name(self):
        return self["user_domain_name"]

    @user_domain_name.setter
    def user_domain_name(self, value):
        self["user_domain_name"] = value

    @property
    def auth_url(self):
        return self["auth_url"]

    @auth_url.setter
    def auth_url(self, value):
        self["auth_url"] = value
