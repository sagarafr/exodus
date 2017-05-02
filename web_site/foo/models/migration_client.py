from web_site.foo.extensions import db
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint


class MigrationClient(db.Model):

    __tablename__ = 'migration_client'

    __table_args__ = (
        PrimaryKeyConstraint('clients_id', 'migrations_id'),
    )
    _clients_id = db.Column('clients_id', postgresql.UUID, ForeignKey("clients.id"), nullable=False)
    _migrations_id = db.Column('migrations_id', postgresql.UUID, ForeignKey("migrations.id"), nullable=False)
    _snapshot_date = db.Column('snapshot_date', db.DateTime(timezone=True), nullable=True)
    _migration_date = db.Column('migration_date', db.DateTime(timezone=True), nullable=True)
    _launch_date = db.Column('launch_date', db.DateTime(timezone=True), nullable=True)

    @property
    def clients_id(self):
        return self._clients_id

    @property
    def migrations_id(self):
        return self._migrations_id

    @property
    def snapshot_date(self):
        return self._snapshot_date

    @snapshot_date.setter
    def snapshot_date(self, value):
        self._snapshot_date = value

    @property
    def migration_date(self):
        return self._migration_date

    @migration_date.setter
    def migration_date(self, value):
        self._migration_date = value

    @property
    def launch_date(self):
        return self._launch_date

    @launch_date.setter
    def launch_date(self, value):
        self._launch_date = value
