import flask
from celery import Celery
from celery.exceptions import Retry
from flask_cors import CORS
from flask_jsonschema import JsonSchema
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from sqlalchemy import event, exc, select
from sqlalchemy.engine import Engine
from flask_admin import Admin


class FlaskCelery(Celery):

    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class AutoRetryTask(TaskBase):
            abstract = True

            @staticmethod
            def backoff(attempts):
                """Return a backoff delay, in seconds, given a number of
                attempts.

                The delay is logarithmic with the number of attempts:
                6, 17, 24, 29, 34, 37, 40, 42, 44, 47...

                """
                import math
                return int(10 * math.log((attempts+2)*(attempts+1)))

            def __call__(self, *args, **kwargs):
                from web_site.foo.tasks import UnrecoverableError
                try:
                    db.session.rollback()
                    return super().__call__(*args, **kwargs)
                except (UnrecoverableError, Retry):
                    raise
                except Exception as error:
                    self.retry(
                        countdown=self.backoff(self.request.retries),
                        exc=error)
                finally:
                    db.session.rollback()

        class ContextTask(AutoRetryTask):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return super().__call__(*args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return super().__call__(*args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.conf.update(app.config.get('CELERY_CONF', {}))

db = SQLAlchemy(session_options={'autoflush': False})
migrate = Migrate()
cel = FlaskCelery('foo', include=['foo.tasks'])
sentry = Sentry()
cors = CORS()
jsonschema = JsonSchema()
admin = Admin()


@event.listens_for(Engine, "engine_connect")
def ping_connection(connection, branch):
    # From http://docs.sqlalchemy.org/en/latest/core/pooling.html
    if branch or connection.should_close_with_result:
        # "branch" refers to a sub-connection of a connection,
        # "should_close_with_result" close request after result
        # we don't want to bother pinging on these.
        return

    try:
        # run a SELECT 1.   use a core select() so that
        # the SELECT of a scalar value without a table is
        # appropriately formatted for the backend
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        # catch SQLAlchemy's DBAPIError, which is a wrapper
        # for the DBAPI's exception.  It includes a .connection_invalidated
        # attribute which specifies if this connection is a "disconnect"
        # condition, which is based on inspection of the original exception
        # by the dialect in use.
        if err.connection_invalidated:
            # run the same SELECT again - the connection will re-validate
            # itself and establish a new connection.  The disconnect detection
            # here also causes the whole connection pool to be invalidated
            # so that all stale connections are discarded.
            connection.scalar(select([1]))
        else:
            raise
