from web_site.foo.controllers import Controller
from web_site.foo.models.client import Client


class ClientController(Controller):

    model_cls = Client
