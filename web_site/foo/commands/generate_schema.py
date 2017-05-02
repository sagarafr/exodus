import json
import os

from flask_script import Command, Option
from ovhschema.schema import Schema, Route
from ovhschema.jsonschema import JsonSchema


class GenerateSchema(Command):
    """Generates an OVH APIv6 schema"""

    option_list = (
        Option('--prefix', '-p', dest='prefix',
               required=False, default='/paas/person',
               help='The entrypoint as exposed to customers via APIv6'),
        Option('--local-prefix', '-l', dest='local_prefix',
               required=False, default='/v6',
               help='The prefix of the routes to include in the schema'),
    )

    def __init__(self, app):
        self.app = app

    def run(self, prefix, local_prefix):

        schemas = self._load_schemas(self.app)

        schema = Schema(prefix, prepend_resource_path=False)
        js = JsonSchema()
        routes_to_add = list()

        for rule in self.app.url_map.iter_rules():

            # Transform URLs from /foo/<id> to /foo/{id}
            endpoint = rule.rule.replace('<', '{').replace('>', '}')

            # Only keep the subset of routes we need the schema from
            if not endpoint.startswith(local_prefix):
                continue

            # Get rid of the /v6 prefix
            endpoint = prefix + endpoint.split(local_prefix)[1]

            # Do not document HEAD and OPTIONS
            methods = [m for m in rule.methods
                       if m in ['GET', 'PUT', 'POST', 'DELETE']]
            method = methods[0]

            description = \
                self.app.view_functions[rule.endpoint].__doc__
            if description:
                description = description.splitlines()[0]
            else:
                description = None

            path_params = []
            for argument in rule.arguments:
                path_params.append({
                    'name': argument,
                    'dataType': 'string',
                    'required': True,
                    'description': self._camel_to_sentence(argument)
                })

            response_type = 'void'
            if rule.response_schema:
                response_schema = self._get_schema(schemas,
                                                   rule.response_schema)
                r = js.process_node(response_schema)
                if ('apiV6_value' in r and
                        'x-ovh-objectName' in response_schema):
                    # created model
                    response_type = response_schema['x-ovh-objectName']
                else:
                    # coretype
                    response_type = r['name']

            body_params = None
            if rule.request_schema:
                request_schema = self._get_schema(schemas,
                                                  rule.request_schema)
                r = js.process_node(request_schema)
                if ('apiV6_value' in r and
                        'x-ovh-objectName' in request_schema):
                    param_type = request_schema['x-ovh-objectName']

                else:
                    param_type = r['name']
                body_params = list()
                body_params.append({
                    'description': request_schema['description'],
                    'dataType': param_type,
                    'paramType': 'body',
                    'required': True
                })

            # Create the schema of the route
            route = Route(
                method=method,
                endpoint=endpoint,
                api_status='BETA',
                description=description,
                path_params=path_params,
                response_type=response_type,
                body_params=body_params
            )
            routes_to_add.append(route)

        schema.models = js.models
        for route in routes_to_add:
            schema.add_route(route)

        # Print the generated schema
        result = self.final_sort(schema.to_dict())
        print(json.dumps(
            result,
            indent=4, separators=(',', ': '), sort_keys=True
        ))

    @staticmethod
    def _camel_to_sentence(text):
        sentence = ''
        for letter in text:
            if letter.isupper():
                sentence += ' '
            sentence += letter.lower()
        return sentence

    @staticmethod
    def _get_schema(schemas, path):
        rv = schemas[path[0]]
        for p in path[1:]:
            rv = rv[p]
        return rv

    @staticmethod
    def _load_schemas(app):
        default_dir = os.path.join(app.root_path, 'jsonschema')
        schema_dir = app.config.get('JSONSCHEMA_DIR', default_dir)
        schemas = {}
        for fn in os.listdir(schema_dir):
            key = fn.split('.')[0]
            fn = os.path.join(schema_dir, fn)
            if os.path.isdir(fn) or not fn.endswith('.json'):
                continue
            with open(fn) as f:
                schemas[key] = json.load(f)
        return schemas

    @classmethod
    def final_sort(cls, to_sort):
        """
        Sort final json to avoid uncomprehensive diff
        I understand this code at 80% but it works
        """
        if isinstance(to_sort, list):
            if all(isinstance(x, dict) for x in to_sort):
                # Sort list of dict
                to_sort.sort(key=lambda x: sorted(str(x)))
            else:
                # Sort list
                to_sort.sort()
            for index, item in enumerate(to_sort):
                to_sort[index] = cls.final_sort(item)
        elif isinstance(to_sort, dict):
            for key, item in to_sort.items():
                to_sort[key] = cls.final_sort(item)
        return to_sort
