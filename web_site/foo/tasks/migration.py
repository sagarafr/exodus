import logging

from web_site.foo.logs import TaskLoggerAdapter
from web_site.foo.extensions import cel


logger = TaskLoggerAdapter(logging.getLogger('celery.task'), dict())


@cel.task(bind=True, name='MIGRATION')
def migration_task(self, client_id):
    # TODO Update the status of the migration and MAKE the migration
    logger.info('MIGRATION UPDATE'.format(client_id), task=self)
    pass
