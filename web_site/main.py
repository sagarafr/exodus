import os

from flask_script import Shell, Manager
from flask_script.commands import ShowUrls
from flask_migrate import MigrateCommand

from web_site.foo import create_app
from web_site.foo.commands.getconfig import GetConfig
from web_site.foo.commands.generate_schema import GenerateSchema
# from web_site.foo.commands.persons import person_manager
from web_site.foo.commands.task_manager import client_task_manager

# TODO make normal (like starter git repo)
app = create_app(
    '/home/arch/exodus/web_site/config-example.yml',
    'dev'
)
manager = Manager(app)


@manager.shell
def make_shell_context():
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('getconfig', GetConfig(app))
manager.add_command('db', MigrateCommand)
manager.add_command('urls', ShowUrls)
manager.add_command('generate-schema', GenerateSchema(app))
manager.add_command('client-task', client_task_manager)
# manager.add_command('persons', person_manager)

if __name__ == '__main__':
    manager.run()
