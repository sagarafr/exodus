import asyncio

from migration_task.resource import *


class ResourceManager:
    def __init__(self):
        self._instance_resource = Resource(resource_type=ResourceType.Instance)
        self._storage_resource = []

    @property
    def instance_resource(self) -> Resource:
        return self._instance_resource

    @instance_resource.setter
    def instance_resource(self, value: Resource):
        self._instance_resource = value
        self._instance_resource.resource_type = ResourceType.Instance

    @property
    def storage_resource(self) -> list:
        return self._storage_resource

    @storage_resource.setter
    def storage_resource(self, value: Resource = Resource()):
        self._storage_resource.append(value)
        self._storage_resource[-1].resource_type = ResourceType.Storage

    def reset_resource(self):
        self._instance_resource = Resource(resource_type=ResourceType.Instance)
        self._storage_resource = []

    def detach_all_volume(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._detach_volumes())
        except:
            raise

    @asyncio.coroutine
    def retrieve_information(self, nova_connection: NovaConnection, cinder_connection: CinderConnection, instance_id: str):
        yield from asyncio.ensure_future(self.instance_resource.init_resource(nova_connection, cinder_connection, instance_id))
        for storage_device in nova_connection.connection.volumes.get_server_volumes(instance_id):
            resource = Resource(resource_type=ResourceType.Storage)
            id_storage = storage_device.to_dict()['id']
            yield from asyncio.ensure_future(resource.init_resource(nova_connection, cinder_connection, id_storage))
            self.storage_resource = resource

    @asyncio.coroutine
    def _detach_volumes(self):
        """
        for storage_device
        yield from asyncio.ensure_future()
        """

    def __str__(self):
        return '\n\n'.join([self._instance_resource.__str__()] + [resource.__str__() for resource in self.storage_resource])
