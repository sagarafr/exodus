from web_site.foo.extensions import db
from web_site.foo.models import BaseModel
from sqlalchemy.dialects import postgresql

"""
CREATE EXTENSION "uuid-ossp";
 
 
CREATE TYPE  status AS ENUM (
    'todo',
    'doing',
    'done',
    'error'
);
  
CREATE TABLE task (
    id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    status status NOT NULL DEFAULT 'todo',
    step character varying(255),
    created_at timestamp with time zone NOT NULL DEFAULT NOW(),
    data jsonb
);
"""


class ClientTask(BaseModel):

    __tablename__ = 'client_task'

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
            'properties': {
                'data': {
                    'type': 'object'
                }
            }
        }
