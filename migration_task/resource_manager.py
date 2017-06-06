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

    def __str__(self):
        return '\n\n'.join([self._instance_resource.__str__()] + [resource.__str__() for resource in self.storage_resource])
