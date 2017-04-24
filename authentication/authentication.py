from utils.ask_credential import ask_credential


class Authentication(dict):
    def __init__(self, **kwargs):
        self["project_id"] = ""
        self["username"] = ""
        self["password"] = ""
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
    def authentication(self):
        return self.project_id, self.username, self.password

    @authentication.setter
    def authentication(self, value):
        self.project_id, self.username, self.password = value

    def import_authentication(self, authentication):
        if authentication.project_id != "":
            self.project_id = authentication.project_id
        if authentication.username != "":
            self.username = authentication.username
        if authentication.password != "":
            self.password = authentication.password

    def ask_credentials(self):
        self.project_id, self.username, self.password = ask_credential([(False, "Project id: "),
                                                                       (False, "User id: "),
                                                                       (True, None)])

    def credentials_to_dict(self):
        credentials = dict([('project_id', self.project_id), ('user_id', self.username), ('password', self.password)])
        if 'token' in self:
            credentials.update(('token', self['token']))
        return credentials


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
