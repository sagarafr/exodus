from flask import redirect, url_for, request
# from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView


class ExtendedModelView(ModelView):

    """Base ModelView of all models."""

    can_edit = True
    can_create = True
    can_export = True
    column_display_pk = False
    column_default_sort = ('id', True)
    page_size = 50
    create_modal = True
    edit_modal = True
    can_view_details = True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index', next=request.url))

    column_exclude_list = ()
    column_details_exclude_list = ()
    form_excluded_columns = ('id', 'created_at', 'updated_at')

    @property
    def column_list(self):
        columns = [col.name for col in self.model.__table__.columns]
        return columns

    def _get_controller(self):
        from web_site.foo.controllers import Controller
        for controller in Controller.__subclasses__():
            if controller.model_cls == self.model:
                return controller
        raise Exception('Controller Not Found')

    def get_column_names(self, only_columns, excluded_columns):
        excluded_columns = getattr(
            self._get_controller(), 'hidden_attributes', ()
        ) + self.column_exclude_list
        excluded_columns = tuple(set(excluded_columns))
        return super().get_column_names(only_columns, excluded_columns)

    def _get_data_from_form(self, form):
        data = {}
        for name, field in form._fields.items():
            field_data = field.data
            if field_data == '':
                field_data = None
            data[name] = field_data
        return data

    def create_model(self, form):
        controller = self._get_controller()
        data = self._get_data_from_form(form)
        return controller._create(data=data)

    def update_model(self, form, model):
        controller = self._get_controller()
        data = self._get_data_from_form(form)
        controller._update(
            model.id,
            data=data
        )
        return True

    def delete_model(self, model):
        controller = self._get_controller()
        controller._delete(model.id)
        return True
