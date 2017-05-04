from web_site.foo.extensions import db
from web_site.foo.models import BaseModel
from sqlalchemy.dialects import postgresql


class ClientTask(BaseModel):
    # TODO CREATE EXTENSION "uuid-ossp"; in sql alchemy
    __tablename__ = 'client_tasks'
    __table_args__ = {'extend_existing': True}

    status = db.Column('status', db.Enum('todo', 'doing', 'done', 'error', name='status'), nullable=False, default='todo')
    step = db.Column('step', db.Enum('snapshot', 'migration', 'launch', name='step'), nullable=False, default='snapshot')
    data = db.Column('data', postgresql.JSONB)

    # TODO make a better data check
    @property
    def _schema(self):
        return {
            'type': 'object',
            'additionalProperties': False,
            'required': ['data'],
            'optional': ['step', 'status'],
            'properties': {
                'data': {
                    'type': 'object'
                },
                'step': {
                    'type': 'string'
                },
                'status': {
                    'type': 'string'
                }
            }
        }

    def change_status(self):
        if self.status == 'todo':
            self.status = 'doing'
        elif self.status == 'doing':
            self.status = 'done'

    def error_status(self):
        self.status = 'error'

    def change_step(self):
        if self.step == 'snapshot':
            self.step = 'migration'
        elif self.step == 'migration':
            self.step = 'launch'
