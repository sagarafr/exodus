from web_site.foo.extensions import db
from web_site.foo.models import BaseModel


class Client(BaseModel):

    __tablename__ = 'clients'
    __repr_fields__ = ('username', 'password', 'auth_url', 'default_domain')

    username = db.Column('username', db.String(255), nullable=False)
    password = db.Column('password', db.String(255), nullable=False)
    auth_url = db.Column('auth_url', db.String(1024), nullable=False)
    default_domain = db.Column('default_domain', db.String(255), default='default', nullable=False)

    @property
    def _schema(self):
        # TODO make a better schema for auth (see RFC) same for password and for default_domain
        return {
            'type': 'object',
            'additionalProperties': False,
            'required': ['username', 'password', 'auth_url'],
            'properties': {
                'username': {
                    'type': 'string',
                    'minLength': 2,
                    'maxLength': 255,
                    'pattern': '^[a-zA-Z0-9_-]+$'
                },
                'password': {
                    'type': 'string',
                    'maxLength': 255,
                    'pattern': '^[a-zA-Z0-9_-]+$'
                },
                'auth_url': {
                    'type': 'string',
                    'pattern': '^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?'
                },
                'default_domain': {
                    'type': 'string',
                    'maxLength': 255,
                    'pattern': '^.+$'
                }
            }
        }
