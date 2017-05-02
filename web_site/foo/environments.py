import os

from raven import Client
from raven.contrib.celery import register_signal

from .extensions import cel, cors, db, migrate, sentry, jsonschema, admin
from .logs import setup_loggers

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    JSON_AS_ASCII = False
    DEBUG = False
    LOGGERS = {}
    CELERY_RETRY_DELAY = 60
    CELERY_CONF = {
        'CELERY_TASK_SERIALIZER': 'json',
        'CELERY_RESULT_SERIALIZER': 'json',
        'CELERY_ACCEPT_CONTENT': ['json'],
        'CELERYD_HIJACK_ROOT_LOGGER': False
    }
    JSONSCHEMA_DIR = os.path.join(basedir, 'schemas')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        cel.init_app(app)
        # TODO: investigate why the application context is  needed
        #   without the context the first test fails and we could not find
        #   the reason. It does not seem the proper way to address the
        #   problem because semantically speaking db.init_app should not need
        #   an application context (which is apparently not used in the code!).
        with app.app_context():
            db.init_app(app)
        migrate.init_app(app, db)
        jsonschema.init_app(app)
        admin.init_app(app)


class DevelopmentConfig(Config):
    DEBUG = True

    @staticmethod
    def init_app(app):
        Config.init_app(app)


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # Needed to prevent flask context errors hiding real errors
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = ''

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        cel.conf.CELERY_ALWAYS_EAGER = True
        cel.conf.BROKER_BACKEND = 'memory'
        cel.conf.CELERY_RESULT_BACKEND = 'cache+memcached://127.0.0.1:11211/'
        # We can't activate this setting right now because chains in eager mode
        # can't be cancelled and thus break the next of the chain raising
        # exceptions even though the the chain is stopped (by an error
        # admittedly). We can either wait for celery to fix this bug or get
        # rid of chains
        # cel.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
        import logging
        logging.getLogger('foo').setLevel(logging.CRITICAL)


class ProductionConfig(Config):
    DEBUG = False
    SENTRY = 'surcharge-me'

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        sentry.init_app(app, dsn=app.config.get('SENTRY'))
        register_signal(Client(dsn=app.config.get('SENTRY')))
        cors.init_app(app)
        setup_loggers(app)


env_config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': ProductionConfig
}
