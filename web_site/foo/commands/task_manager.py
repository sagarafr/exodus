from web_site.foo.commands import ManagerWithDefaultCommands
from web_site.foo.controllers.client_task import ClientTaskController

# TODO test this
client_task_manager = ManagerWithDefaultCommands(
    controller_cls=ClientTaskController,
    description='Perform actions on Task',
    default_command=('list', 'show', 'delete'))
