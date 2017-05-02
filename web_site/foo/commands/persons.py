from web_site.foo.commands import ManagerWithDefaultCommands
from web_site.foo.controllers import PersonController

person_manager = ManagerWithDefaultCommands(
    controller_cls=PersonController,
    description='Perform actions on Persons',
    default_command=('list', 'show', 'delete'))
