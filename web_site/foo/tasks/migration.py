import logging
import datetime
from authentication.authentication import AuthenticationV3
from migration.snapshot import make_snapshot
from migration.migration import migration
from migration.launch_instance import launch_instance
from utils.get_ids import get_ovh_default_nics
from shell.shell import Connections
from shell.shell import ConnectionsVersion
from web_site.foo.logs import TaskLoggerAdapter
from web_site.foo.extensions import cel
from web_site.foo.extensions import db
from web_site.foo.models.client_task import ClientTask


logger = TaskLoggerAdapter(logging.getLogger('celery.task'), dict())


@cel.task(bind=True, name='MIGRATION', ignore_result=True)
def migration_task(self, id_task):
    # TODO Update the status of the migration and MAKE the migration
    # TODO change this to get the possibility of machine_id and not machine_name only
    # TODO make this with pipe
    data = ClientTask.query.get(id_task)
    data = dict(data.data)

    region_from, machine_from, region_to, machine_to, flavor_to = data['from']['region'], data['from']['machine_name'], data['to']['region'], data['to']['machine_name'], data['to']['flavor']
    creds_src, creds_dest = _get_creds_from_database(data)
    connection_src = Connections(AuthenticationV3(**creds_src), ConnectionsVersion())
    snapname = machine_from + str(datetime.datetime.now().isoformat())
    connection_dest = connection_src
    if creds_src != creds_dest:
        connection_dest = Connections(AuthenticationV3(**creds_src), ConnectionsVersion())

    task = ClientTask.query.with_lockmode('update').get(id_task)
    task.change_status()
    db.session.add(task)
    db.session.commit()
    make_snapshot(connection_src.get_nova_connection(region_from), machine_from, snapname)
    task = ClientTask.query.with_lockmode('update').get(id_task)
    task.change_step()
    db.session.add(task)
    db.session.commit()

    # TODO change this with the machine capabilities
    migration(connection_src.get_glance_connection(region_from),
              connection_dest.get_glance_connection(region_to), snapname, snapname, "qcow2", "bare")
    task = ClientTask.query.with_lockmode('update').get(id_task)
    task.change_step()
    db.session.add(task)
    db.session.commit()

    launch_instance(connection_dest.get_nova_connection(region_to), machine_to, snapname, flavor_to, get_ovh_default_nics(connection_dest.get_neutron_connection(region_to)))
    task = ClientTask.query.with_lockmode('update').get(id_task)
    task.change_status()
    db.session.add(task)
    db.session.commit()


def _get_creds_from_database(data: dict):
    return _get_creds(data['from']), _get_creds(data['to'])


def _get_creds(data: dict):
    return {'username': data.get('username'), 'password': data.get('password'), 'auth_url': data.get('auth_url')}
