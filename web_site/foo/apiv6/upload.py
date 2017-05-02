from web_site.foo.apiv6 import api
from web_site.foo.apiv6 import get_payload
from web_site.main import app
from flask import request
from flask import flash
from tempfile import NamedTemporaryFile
from os import path
from os import remove
from web_site.main import app
from web_site.foo.controllers.client import ClientController
from web_site.foo.apiv6 import single_object


CLIENT_VISIBLE = ['id']


@api.route('/migrate', methods=['POST'])
def migrate():
    app.logger.info(request)
    if request.method == 'POST':
        data = {'username': None, 'password': None, 'auth_url': None, 'default_domain': None}
        try:
            data = get_payload()
        except:
            app.logger.info("Have no playload informations")
        if 'file' in request.files:
            app.logger.info(request.files['file'])
            _save(request.files['file'], data)
        client = ClientController.create(data)
        return single_object(client, CLIENT_VISIBLE, status_code=200)


def _save(file, store_data: dict):
    dest_filename = path.join(app.config['UPLOAD_FOLDER'], NamedTemporaryFile().name)
    file.save(dest_filename)
    with open(dest_filename, 'r') as fd_filename:
        for line in fd_filename:
            _store_element(line, 'OS_USERNAME', store_data, 'username')
            _store_element(line, 'OS_PASSWORD', store_data, 'password')
            _store_element(line, 'OS_AUTH_URL', store_data, 'auth_url')
            _store_element(line, 'OS_DEFAULT_DOMAIN', store_data, 'default_domain')
    remove(dest_filename)
    if store_data['default_domain'] is None:
        del store_data['default_domain']
    return store_data


def _store_element(line: str, pattern: str, store_data: dict, key_store_data: str):
    # TODO : remove all spaces at the beginning and find the # and escape the line
    line = line.rstrip('\n')
    index = line.find(pattern)
    if index != -1:
        line = line[index + len(pattern):]
        index = line.find('=')
        if index != -1:
            line = line[index + len('='):]
            # TODO replace " at the beginning and at the end of file
            line = line.replace('"', '')
            store_data[key_store_data] = line
