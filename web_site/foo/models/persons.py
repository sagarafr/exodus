from ..extensions import db
from . import BaseModel


class Person(BaseModel):

    __tablename__ = 'persons'
    __repr_fields__ = ('name', 'age')

    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, default=0, nullable=False)

    @property
    def _schema(self):
        return {
            'type': 'object',
            'additionalProperties': False,
            'required': ['name', 'age'],
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 2,
                    'maxLength': 255,
                    'pattern': '^[a-zA-Z0-9_-]+$'
                },
                'age': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 120
                }
            }
        }

    def increase_age(self):
        self.age += 1
