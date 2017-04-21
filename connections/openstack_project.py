import utils.ask_credential as credential


class OpenStackProject(object):
    def __init__(self, project_id: str = "", user_id: str = "", password: str = "", token: str = ""):
        self._project_id = project_id
        self._user_id = user_id
        self._password = password
        self._token = token

    def to_dict(self):
        return {'project_id': self.project_id, 'username': self.user_id, 'password': self.password, 'token': self.token}

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self, value):
        self._project_id = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    def ask_credentials(self):
        self.project_id, self.user_id, self.password = credential.ask_credential([(False, "Project id: "),
                                                                                  (False, "User id: "),
                                                                                  (True, None)])
