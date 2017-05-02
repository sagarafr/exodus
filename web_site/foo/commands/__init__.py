import yaml
import json
import sys
import prettytable

from flask_script import Command, Manager, Option

from web_site.foo import ExtendedJSONEncoder


class ManagerWithDefaultCommands(Manager):
    """Manager injecting default commands on controller commands."""

    def __init__(self, controller_cls,
                 default_command=('show', 'list', 'delete'),
                 *args, **kwargs):
        self.controller_cls = controller_cls
        self.default_command = default_command
        kwargs['with_default_commands'] = True
        super().__init__(*args, **kwargs)
        self.set_defaults()

    def add_default_commands(self):
        for command in self.default_command:
            if command in self._commands:
                continue
            if 'show' == command:
                self.add_command('show', ShowCommand)
            elif 'list' == command:
                self.add_command('list', ListCommand)
            elif 'delete' == command:
                self.add_command('delete', DeleteCommand)
            else:
                raise Exception('default command {} '
                                'was not implemented'.format(command))

    def add_command(self, name, command, **kwargs):
        if issubclass(command, ControllerCommand):
            command = command(controller_cls=self.controller_cls)
        super().add_command(name, command, **kwargs)


class ExtendedCommand(Command):

    def display(self, *args, **kwargs):
        print(*args, **kwargs)


class ControllerCommand(ExtendedCommand):
    """Base class of all Commands linked to a model controller."""

    get_model_by = 'name'

    def __init__(self, controller_cls, *args, **kwargs):
        self.controller_cls = controller_cls
        super().__init__(*args, **kwargs)

    def get_options(self):
        """Aggregate all options defined in the command ancestry."""
        options = []
        for cls in self.__class__.mro():
            opts = list(getattr(cls, 'option_list', []))
            options.extend(opts)

        # Deduplicate the options
        return list(set(options))

    def get_model(self, name_or_id, get_model_by=None, controller=None):
        controller = controller or self.controller_cls
        model_class_name = controller.model_cls.__name__
        name_or_id = name_or_id.strip()
        if name_or_id.isdigit():
            try:
                model = controller.get(name_or_id)
            except controller.NotFoundError:
                self.display(
                    '%s %s not found' % (model_class_name, name_or_id))
                return
        else:
            try:
                model = controller.get(name_or_id)
            except controller.NotFoundError:
                self.display(
                    '%s %s not found' % (model_class_name, name_or_id))
                return
        return model

    def list_models(self, order_by, limit, reverse, controller=None, **kwargs):
        controller = controller or self.controller_cls
        return controller.list(
            order_by=order_by,
            limit=limit,
            reverse=reverse,
            **kwargs)

    def delete_model(self, name_or_id, controller=None):
        controller = controller or self.controller_cls
        return controller.delete(name_or_id)

    def format_models(self, models, format):
        if not models:
            self.display('No model found', file=sys.stderr)
        elif format == 'json':
            self.display(json.dumps(models, ensure_ascii=False, sort_keys=True,
                                    indent=2, cls=ExtendedJSONEncoder))
        elif format == 'yaml':
            self.display(yaml.dump(models, default_flow_style=False))
        elif format == 'table':
            self.display(self.models_to_table(models))

    def models_to_table(self, models):
        models = [models] if not isinstance(models, list) else models
        table = prettytable.PrettyTable()
        columns = [k for k in sorted(models[0].keys())
                   if k not in {'id', 'updated_at', 'created_at'}]
        columns = ['id'] + columns + ['updated_at', 'created_at']
        table._set_field_names(columns)
        for model in models:
            table.add_row([model[col] for col in columns])
        return table


class ControllerDisplayCommand(ControllerCommand):
    """Base class of all commands doing display (list/show)."""

    option_list = (
        Option('--format', type=str, default='table',
               choices=('json', 'yaml', 'table')),
    )


class ShowCommand(ControllerDisplayCommand):
    """Display the object"""

    option_list = (
        Option('name_or_id', type=str, help='The name or id of the model'),
    )

    def run(self, name_or_id, format):
        model = self.get_model(name_or_id)
        if model:
            self.format_models(model, format)


class ListCommand(ControllerDisplayCommand):
    """List objects"""

    option_list = (
        Option('--order-by', type=str,
               help='The field by which to order the results'),
        Option('-r', '--reverse', action='store_true',
               help='Whether to reverse the results order'),
        Option('--limit', type=int, default=20,
               help='The maximum amount of returned results')
    )

    def run(self, order_by, reverse, limit, format, **filters):
        models = self.list_models(
            order_by=order_by,
            limit=limit,
            reverse=reverse,
            filters=filters)
        if models:
            self.format_models(models, format)


class DeleteCommand(ControllerCommand):
    """Schedule a stack deletion."""

    option_list = (
        Option('name_or_id', type=str, help='The name or id of the model'),
    )

    def run(self, name_or_id):
        self.delete_model(name_or_id)


def sub_opts(app, **kwargs):
    pass


class ShowUrls(ExtendedCommand):
    """
        Displays all of the url matching routes for the project
    """

    def run(self):
        from flask import current_app

        rows = []
        column_headers = ('Rule', 'Method', 'Endpoint')

        rules = sorted(current_app.url_map.iter_rules(),
                       key=lambda rule: getattr(rule, 'rule'))
        for rule in rules:
            method = [m for m in rule.methods
                      if m not in ('HEAD', 'OPTIONS')][0]
            rows.append((rule.rule, method, rule.endpoint))
        column_length = 4

        str_template = ''
        table_width = 0

        if column_length >= 1:
            max_rule_length = max(len(r[0]) for r in rows)
            max_rule_length = max_rule_length if max_rule_length > 4 else 4
            str_template += '%-' + str(max_rule_length) + 's'
            table_width += max_rule_length

        if column_length >= 2:
            max_endpoint_length = max(len(str(r[1])) for r in rows)
            # max_endpoint_length = max(rows, key=len)
            max_endpoint_length = max_endpoint_length \
                if max_endpoint_length > 8 else 8
            str_template += '  %-' + str(max_endpoint_length) + 's'
            table_width += 2 + max_endpoint_length

        if column_length >= 3:
            max_arguments_length = max(len(str(r[2])) for r in rows)
            max_arguments_length = max_arguments_length \
                if max_arguments_length > 9 else 9
            str_template += '  %-' + str(max_arguments_length) + 's'
            table_width += 2 + max_arguments_length

        self.display(str_template % (column_headers[:column_length]))
        self.display('-' * table_width)

        for row in rows:
            self.display(str_template % row[:column_length])
