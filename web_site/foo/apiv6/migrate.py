from flask import request
from keystoneauth1.exceptions.connection import ConnectFailure
from web_site.main import app
from web_site.foo.apiv6 import api
from web_site.foo.apiv6 import single_object
from web_site.foo.apiv6.errors import format_error
from web_site.foo.controllers.client_task import ClientTaskController
from authentication.authentication import AuthenticationV3
from shell.shell import Connections
from shell.shell import ConnectionsVersion
from utils.check_exitence import check_existence
from copy import deepcopy


@api.route('/migrate', methods=['POST'])
def post_migrate():
    """Create entry in the database"""
    try:
        if not _check_data():
            return format_error(400, 'The server did not understand your request')
    except ConnectFailure as failure_message:
        app.logger.info(failure_message)
        return format_error(404, "The requested resource could not be found")
    data = {'data': {
        'from': dict(request.json['from']),
        'to': dict(request.json['to'])}
    }
    client_task = ClientTaskController.create(data)
    app.logger.info(client_task)
    return single_object(client_task, ['id'])


@api.route('/migrate/<string:id_task>', methods=['GET'])
def get_migrate(id_task: str):
    """Get all instance in details"""
    creds_src, creds_dest = _get_creds_from_database(id_task)
    response = {'from': dict(), 'to': dict()}
    connection_src = Connections(AuthenticationV3(**creds_src), ConnectionsVersion())
    for region_from in connection_src.nova:
        response['from'].update({region_from: [s.to_dict() for s in connection_src.nova[region_from].connection.servers.list()]})
    if creds_src != creds_dest:
        connection_dest = Connections(AuthenticationV3(**creds_dest), ConnectionsVersion())
        for region_to in connection_dest.nova:
            response['to'].update({region_to: [s.to_dict() for s in connection_src.nova[region_to].connection.servers.list()]})
    else:
        response['to'] = deepcopy(response['from'])
    return single_object(response, ['from', 'to'])


@api.route('/migrate/<string:id_task>/instance', methods=['GET'])
def get_migrate_instance(id_task: str):
    """Get all instances name"""
    creds_src, creds_dest = _get_creds_from_database(id_task)
    response = {'from': dict(), 'to': dict()}
    connection_src = Connections(AuthenticationV3(**creds_src), ConnectionsVersion())
    for region_from in connection_src.nova:
        response['from'].update({region_from: [s.to_dict()['name'] for s in connection_src.nova[region_from].connection.servers.list()]})
        if creds_src != creds_dest:
            connection_dest = Connections(AuthenticationV3(**creds_dest), ConnectionsVersion())
            for region_to in connection_dest.nova:
                response['to'].update({region_to: [s.to_dict()['name'] for s in connection_src.nova[region_to].connection.servers.list()]})
        else:
            response['to'] = deepcopy(response['from'])
    return single_object(response, ['from', 'to'])


@api.route('/migrate/<string:id_task>/flavor', methods=['GET'])
def get_migrate_flavor(id_task: str):
    """Get all flavors name"""
    creds_src, creds_dest = _get_creds_from_database(id_task)
    response = {'from': dict(), 'to': dict()}
    connection_src = Connections(AuthenticationV3(**creds_src), ConnectionsVersion())
    for region_from in connection_src.nova:
        response['from'].update({region_from: [s.to_dict()['name'] for s in connection_src.nova[region_from].connection.flavors.list()]})
        if creds_src != creds_dest:
            connection_dest = Connections(AuthenticationV3(**creds_dest), ConnectionsVersion())
            for region_to in connection_dest.nova:
                response['to'].update({region_to: [s.to_dict()['name'] for s in connection_src.nova[region_to].flavors.servers.list()]})
        else:
            response['to'] = deepcopy(response['from'])
    return single_object(response, ['from', 'to'])


@api.route('/migrate/<string:id_task>/start', methods=['POST'])
def post_migrate_start(id_task: str):
    """Start the migration"""
    client, _ = ClientTaskController.async_migration(id_task)
    return single_object(client, ['status', 'step'], 200)


@api.route('/migrate/<string:id_task>/status', methods=['GET'])
def get_migration_status(id_task: str):
    """Get the migration status"""
    client = ClientTaskController.get(id_task)
    return single_object(client, ['status', 'step'])


def _get_creds_from_database(id_task: str):
    client = ClientTaskController.get(id_task)
    client = client['data']
    app.logger.info(client)
    return _get_creds(client['from']), _get_creds(client['to'])


def _check_data():
    first_keys = ['from', 'to']
    second_keys = ['username', 'password', 'auth_url', 'type']
    if request.is_json and check_existence(request.json, first_keys) and check_existence(request.json['from'], second_keys) and check_existence(request.json['to'], second_keys):
        creds = _get_creds(request.json['from'])
        AuthenticationV3(**creds)
        creds = _get_creds(request.json['to'])
        AuthenticationV3(**creds)
        return True
    return False


def _get_creds(data: dict):
    return {'username': data.get('username'), 'password': data.get('password'), 'auth_url': data.get('auth_url')}
