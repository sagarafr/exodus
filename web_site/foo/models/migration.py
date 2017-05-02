from web_site.foo.extensions import db
from web_site.foo.models import BaseModel
from sqlalchemy.dialects import postgresql


class Migration(BaseModel):
    __tablename__ = 'migrations'
    __repr_fields__ = ('status', 'step')

    _status = db.Column('status', postgresql.ENUM('to_do', 'doing', 'done', name='status'), nullable=False)
    _step = db.Column('step', postgresql.ENUM('snapshot', 'migration', 'launch', 'error', name='step'), nullable=False)

    @property
    def _schema(self):
        return {
            'type': 'object',
            "additionalProperties": False,
            "required": ['status', 'step'],
            'properties': {
                'status': {
                    'type': 'string',
                    'pattern': '^(to_do, doing, done)$'
                },
                'step': {
                    'type': 'string',
                    'pattern': '^(snapshot, migration, launch, error)$'
                }
            }
        }

    def next_status(self):
        if self.status == "to_do":
            self.status = "doing"
        elif self.status == "doing":
            self.status = "done"

    def next_step(self):
        if self.step == "snapshot":
            self.step = "migration"
        elif self.step == "migration":
            self.step = "launch"

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value
