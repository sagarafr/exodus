import codecs
import yaml
import json
import os
import importlib
import pkgutil
import datetime

from flask import Flask
from flask.wrappers import Request
from flask.json import JSONEncoder
from flask.app import _logger_lock
from werkzeug.routing import Rule

from web_site.foo.environments import env_config
from web_site.foo.logs import setup_loggers, FlaskLoggerAdapter


MODULES_TO_IMPORT = ('models', 'tasks', 'main', 'apiv6', 'doc', 'admin')


class ExtendedRequest(Request):
    @property
    def json(self):
        return self.get_json(force=True)


class ExtendedRule(Rule):

    def __init__(self, *args, **kwargs):
        self.request_schema = kwargs.pop('request_schema', None)
        self.response_schema = kwargs.pop('response_schema', None)
        super().__init__(*args, **kwargs)


class ExtendedJSONEncoder(JSONEncoder):
    """JSON encoder that transforms datetimes to RFC 3339"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return JSONEncoder.default(self, o)


class ExtendedFlask(Flask):
    request_class = ExtendedRequest
    url_rule_class = ExtendedRule
    json_encoder = ExtendedJSONEncoder

    @property
    def logger(self):
        if self._logger and self._logger.name == self.logger_name:
            return self._logger
        with _logger_lock:
            if self._logger and self._logger.name == self.logger_name:
                return self._logger
            from flask.logging import create_logger
            self._logger = rv = FlaskLoggerAdapter(create_logger(self), dict())
            return rv


def create_app(config_file='config.yml', environment='default'):
    app = ExtendedFlask(__name__)

    # Load default vars for env
    app.config.from_object(env_config[environment])

    # Load vars for conf file
    data_file = read_config(config_file)
    app.config.update(data_file)
    app.config['CELERY_CONF'].update(env_config[environment].CELERY_CONF)

    # Load env's extension
    env_config[environment].init_app(app)

    from web_site.foo.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from web_site.foo.apiv6 import api as apiv6_blueprint
    app.register_blueprint(apiv6_blueprint, url_prefix='/v6')

    from web_site.foo.doc import doc as doc_blueprint
    app.register_blueprint(doc_blueprint, url_prefix='/doc')

    return app


def read_config(config_file, verbose=False):
    # Locate the config file to use
    if not os.path.isfile(config_file):
        print('Missing configuration file')
        return {}
    if verbose:
        print('Using configuration file: %s' % config_file)

    # Open and read the config file
    with codecs.open(config_file, 'r', 'utf8') as file_handler:
        conf = yaml.load(file_handler)
    if conf is None:
        conf = {}
    if verbose:
        print(json.dumps(conf, sort_keys=True,
                         indent=4, separators=(',', ': ')))
    return conf


def import_submodules(package, modules_to_import):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if not name.startswith("_") and not name.startswith("tests"):
            full_name = package.__name__ + '.' + name

            if any((x in package.__name__ for x in modules_to_import)):
                results[full_name] = importlib.import_module(full_name)

            elif any((x in name for x in modules_to_import)):
                results[full_name] = importlib.import_module(full_name)

            if is_pkg and name in modules_to_import:
                results.update(import_submodules(full_name, modules_to_import))
    return results

import_submodules(__name__, MODULES_TO_IMPORT)
