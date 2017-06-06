import asyncio

from connections.connections import Connections
from migration_task.resource_manager import ResourceManager
from migration_task.resource import *


class MigrationManager:
    def __init__(self, **kwargs):
        try:
            self._source_connection = kwargs['source_connection']
            self._destination_connection = kwargs['destination_connection']
        except Exception as exception_message:
            print(exception_message)
            raise
        self._resource_manager = ResourceManager()
        self._source_region_name = None
        self._destination_region_name = None
        self._instance_id = None

    @property
    def resource_manager(self) -> ResourceManager:
        return self._resource_manager

    @property
    def source_connection(self) -> Connections:
        return self._source_connection

    @property
    def destination_connection(self) -> Connections:
        return self.destination_connection

    @property
    def source_region_name(self) -> str:
        return self._source_region_name

    @property
    def destination_region_name(self) -> str:
        return self._destination_region_name

    @property
    def instance_id(self) -> str:
        return self._instance_id

    def prepare_migration(self, instance_id: str, region_name_source: str, region_name_destination: str):
        self._source_region_name = region_name_source
        self._destination_region_name = region_name_destination
        self._instance_id = instance_id
        self.resource_manager.reset_resource()
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._retrieve_information())
        except:
            raise

    @asyncio.coroutine
    def _retrieve_information(self):
        nova_connection = self.source_connection.get_nova_connection(self._source_region_name)
        cinder_connection = self.source_connection.get_cinder_connection(self._source_region_name)
        instance_resource = self.resource_manager.instance_resource
        yield from asyncio.ensure_future(instance_resource.init_resource(nova_connection, cinder_connection, self._instance_id))
        for storage_device in nova_connection.connection.volumes.get_server_volumes(self._instance_id):
            self.resource_manager.storage_resource = Resource()
            resource = self.resource_manager.storage_resource[-1]
            id_storage = storage_device.to_dict()['id']
            yield from asyncio.ensure_future(resource.init_resource(nova_connection, cinder_connection, id_storage))
