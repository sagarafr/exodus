"""
import logging
from web_site.foo.logs import TaskLoggerAdapter
from migration.snapshot import make_snapshot_from_uuid
from connections.nova_connection import NovaConnection


from web_site.foo.extensions import cel
from web_site.foo.extensions import db

logger = TaskLoggerAdapter(logging.getLogger('celery.task'), dict())


@cel.tasks(bind=True, name='MAKE_SNAPSHOT')
def make_snapshot(self, nova_connection: NovaConnection, server_uuid: str, snapshot_name: str):
    logger.info("Make a snapshot from:\n\
                *Connection : {0}\n\
                *Server uuid source : {1}\n\
                *Snapshot name : {2}\n".format(str(nova_connection), server_uuid, snapshot_name))
    make_snapshot_from_uuid(nova_connection, server_uuid, snapshot_name)
"""