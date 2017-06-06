from enum import Enum
from json import dumps
import asyncio

from connections.nova_connection import NovaConnection
from connections.cinder_connection import CinderConnection


class ResourceType(Enum):
    Instance = 1
    Storage = 2
    Undefined = 3


class Resource:
    def __init__(self, resource_information: dict = None, snapshot_name: str = None, resource_created: dict = None,
                 resource_type: ResourceType = None):
        self._resource_information = {} if resource_information is None else resource_information
        self._snapshot_name = "" if snapshot_name is None else snapshot_name
        self._resource_created = {} if resource_created is None else resource_created
        self._resource_type = ResourceType.Undefined if resource_type is None else resource_type

    @property
    def resource_information(self) -> dict:
        return self._resource_information

    @resource_information.setter
    def resource_information(self, value: dict):
        self._resource_information = value

    @property
    def snapshot_name(self) -> str:
        return self._snapshot_name

    @snapshot_name.setter
    def snapshot_name(self, value: str):
        self._snapshot_name = value

    @property
    def resource_created(self) -> dict:
        return self._resource_created

    @resource_created.setter
    def resource_created(self, value: dict):
        self._resource_created = value

    @property
    def resource_type(self) -> ResourceType:
        return self._resource_type

    @resource_type.setter
    def resource_type(self, value: ResourceType):
        self._resource_type = value

    @asyncio.coroutine
    def init_resource(self, nova_connection: NovaConnection, cinder_connection: CinderConnection, resource_id: str):
        try:
            if self.resource_type is ResourceType.Instance:
                self.resource_information = nova_connection.connection.servers.get(resource_id).to_dict()
            elif self.resource_type is ResourceType.Storage:
                self.resource_information = cinder_connection.connection.volumes.get(resource_id).to_dict()
        except:
            raise

    def __str__(self):
        return "resource_information: " + dumps(self.resource_information, indent=4) + '\n' + \
               "snapshot_name: " + self.snapshot_name.__str__() + '\n' + \
               "resource_created: " + dumps(self.resource_created, indent=4) + '\n' + \
               "resource_type: " + self.resource_type.__str__() + '\n'
