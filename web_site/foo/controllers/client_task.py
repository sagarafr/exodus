from web_site.foo.controllers import Controller
from web_site.foo.models.client_task import ClientTask
from web_site.foo.tasks.migration import migration_task


class ClientTaskController(Controller):

    model_cls = ClientTask

    @classmethod
    def async_migration(cls, id_task: str):
        client = cls.get(id_task)
        tasks = cls.schedule_task(migration_task, client)
        return client, tasks
