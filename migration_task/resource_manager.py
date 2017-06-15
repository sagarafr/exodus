from migration_task.resource import *

import asyncio
import concurrent.futures


class ResourceManager:
    """
    ResourceManager manager all resource of one instance
    """
    def __init__(self):
        """
        Initialize the instance and storage resource instance 
        """
        self._instance_resource = Resource(resource_type=ResourceType.Instance)
        self._storage_resource = []

    @property
    def instance_resource(self) -> Resource:
        """
        Instance resource property

        :return: Resource 
        """
        return self._instance_resource

    @instance_resource.setter
    def instance_resource(self, value: Resource):
        """
        Set the instance resource 
        
        :param value: Resource that content the instance resource
        """
        self._instance_resource = value
        self._instance_resource.resource_type = ResourceType.Instance

    @property
    def storage_resource(self) -> list:
        """
        List of storage resource property

        :return: list of Resource 
        """
        return self._storage_resource

    @storage_resource.setter
    def storage_resource(self, value: Resource = Resource()):
        """
        Add a resource at the end of list
        
        :param value: Resource to add
        """
        self._storage_resource.append(value)
        self._storage_resource[-1].resource_type = ResourceType.Storage

    def reset_resource(self):
        """
        Reset all data inside of ResourceManager
        """
        self._instance_resource = Resource(resource_type=ResourceType.Instance)
        self._storage_resource = []

    @asyncio.coroutine
    def detach_all_volume(self, nova_connection: NovaConnection):
        """
        Detach all volume in asynchronous mode
        
        :param nova_connection: NovaConnection to detach all volume
        """
        asyncio.ensure_future(self._detach_all_volumes(nova_connection))

    @asyncio.coroutine
    def retrieve_information(self, nova_connection: NovaConnection, cinder_connection: CinderConnection, instance_id: str):
        """
        Retrieve all information in order to initialize all resource information
        
        :param nova_connection: NovaConnection situated in the same region that instance_id
        :param cinder_connection: CinderConnection situated in the same region that instance_id
        :param instance_id: str content the id of the instance
        """
        yield from asyncio.ensure_future(self.instance_resource.init_resource(nova_connection, cinder_connection, instance_id))
        for storage_device in nova_connection.connection.volumes.get_server_volumes(instance_id):
            resource = Resource(resource_type=ResourceType.Storage)
            id_storage = storage_device.to_dict()['id']
            yield from asyncio.ensure_future(resource.init_resource(nova_connection, cinder_connection, id_storage))
            self.storage_resource = resource

    def migration(self, nova_connection_source: NovaConnection, glance_connection_source: GlanceConnection,
                  glance_connection_destination: GlanceConnection, nova_connection_destination: NovaConnection,
                  neutron_connection_destination: NeutronConnection, cinder_connection_source: CinderConnection,
                  cinder_connection_destination: CinderConnection):
        """
        Migrate the instance

        :param nova_connection_source: NovaConnection at the region source
        :param glance_connection_source: GlanceConnection at the region source
        :param glance_connection_destination: GlanceConnection at the region destination
        :param nova_connection_destination: NovaConnection at the region destination
        :param neutron_connection_destination: Neutron at the region destination
        :param cinder_connection_source: CinderConnection at the region source
        :param cinder_connection_destination: CinderConnection at the region destination
        """
        # TODO change the max_workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as thread_pool:
            thread_pool.submit(self.instance_resource.migration, nova_connection_source, glance_connection_source,
                               glance_connection_destination, nova_connection_destination,
                               neutron_connection_destination, cinder_connection_source,
                               cinder_connection_destination)
            for storage_device in self.storage_resource:
                thread_pool.submit(storage_device.migration, nova_connection_source, glance_connection_source,
                                   glance_connection_destination, nova_connection_destination,
                                   neutron_connection_destination, cinder_connection_source,
                                   cinder_connection_destination)

    @asyncio.coroutine
    def _detach_all_volumes(self, nova_connection: NovaConnection):
        for storage_device in self.storage_resource:
            yield from asyncio.ensure_future(self._detach_a_volume(nova_connection, storage_device['id']))

    @asyncio.coroutine
    def _detach_a_volume(self, nova_connection: NovaConnection, volume_id: str):
        try:
            nova_connection.connection.volumes.delete_server_volume(self.instance_resource.resource_information['id'], volume_id)
        except:
            raise

    def __str__(self):
        return '\n\n'.join([self._instance_resource.__str__()] + [resource.__str__() for resource in self.storage_resource])
