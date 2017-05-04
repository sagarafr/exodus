import os
import contextlib

from flask_testing import TestCase

from web_site.foo import create_app
from web_site.foo.extensions import db


class FunctionalTest(TestCase):
    """Initialize Flask app and db for functional tests.

    For each class creates the Flask app and set up the database.
    Before each test truncate the content of the database, but keep the schema.
    """

    @classmethod
    def create_standalone_app(cls):
        return create_app(
            environment='test',
            config_file=os.getenv('APP_CONFIG') or 'config.yml'
        )

    def create_app(self):
        self.app = self.create_standalone_app()
        return self.app

    @classmethod
    def setUpClass(cls):
        with cls.create_standalone_app().app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.create_standalone_app().app_context():
            db.drop_all()

    def setUp(self):
        db.session.rollback()
        with contextlib.closing(db.engine.connect()) as con:
            trans = con.begin()
            con.execute('TRUNCATE {} RESTART IDENTITY;'.format(
                ','.join(table.name
                         for table in reversed(db.get_tables_for_bind()))))
            trans.commit()

    def tearDown(self):
        db.session.remove()
