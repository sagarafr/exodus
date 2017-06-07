from connections.connections import Connections
from migration_task.resource_manager import ResourceManager
from utils.attach_a_volume import attach_a_volume

import asyncio


class MigrationManager:
    """
    MigrationManager manage a migration task. This class make a migration between 2 regions
    
    First of all, you must call prepare_migration then you can call migration method
    Caution it is one MigrationManager for one instance to migrate for the moment
    """
    def __init__(self, **kwargs):
        """
        :param source_connection: Connections object content all source connections
        :param destination_connection: Connections object content all destination connections
        :raise Exception: If he doesnt found parameter value
        """
        try:
            self._source_connection = kwargs['source_connection']
            self._destination_connection = kwargs['destination_connection']
        except Exception:
            raise
        self._resource_manager = ResourceManager()
        self._source_region_name = None
        self._destination_region_name = None
        self._instance_id = None

    @property
    def resource_manager(self) -> ResourceManager:
        """
        ResourceManager property

        :return: ResourceManager of the object
        """
        return self._resource_manager

    @property
    def source_connection(self) -> Connections:
        """
        Source connections property
        
        :return: Connections of the object 
        """
        return self._source_connection

    @property
    def destination_connection(self) -> Connections:
        """
        Destination connections property
        
        :return: Connections of the object
        """
        return self._destination_connection

    @property
    def source_region_name(self) -> str:
        """
        Source region name property
        
        :return: str content the source region name 
        """
        return self._source_region_name

    @property
    def destination_region_name(self) -> str:
        """
        Destination region name property

        :return: str content the destination region name 
        """
        return self._destination_region_name

    @property
    def instance_id(self) -> str:
        """
        Instance id property
        
        :return: str content the instance id
        """
        return self._instance_id

    def prepare_migration(self, instance_id: str, region_name_source: str, region_name_destination: str):
        """
        Prepare the migration for an instance_id. This instance is in the region_name_source and will be transfer in
        region_name_destination
        
        :param instance_id: str id of the instance
        :param region_name_source: str the region name source
        :param region_name_destination: str the region name destination
        :raise: If something have failed
        """
        self._source_region_name = region_name_source
        self._destination_region_name = region_name_destination
        self._instance_id = instance_id
        self.resource_manager.reset_resource()
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._retrieve_information())
        except:
            raise

    def migration(self):
        """
        Migrate the instance register earlier
        """
        nova_connection_destination = self.destination_connection.get_nova_connection(self.destination_region_name)
        cinder_connection_destination = self.destination_connection.get_cinder_connection(self.destination_region_name)
        self._make_migration()
        status = nova_connection_destination.connection.servers.get(self.resource_manager.instance_resource.resource_created['id']).to_dict()['status']
        # TODO make the status in the right way
        while status != 'ACTIVE':
            status = nova_connection_destination.connection.servers.get(
                self.resource_manager.instance_resource.resource_created['id']).to_dict()['status']
        disk_device_attached = False
        # TODO attach the disk in an other function
        while not disk_device_attached:
            disk_device_attached = True
            for storage_resource in self.resource_manager.storage_resource:
                disk_information = cinder_connection_destination.connection.volumes.get(storage_resource.resource_created['id']).to_dict()
                if disk_information['status'] == 'available':
                    attach_a_volume(nova_connection_destination, self.resource_manager.instance_resource.resource_created['id'], disk_information['id'])
                elif disk_information['status'] != 'in-use':
                    disk_device_attached = False
        print(self.resource_manager.instance_resource)

    def detach_all_volumes(self):
        """
        Detach all volume of the instance given
        :raise: Exception if something go wrong
        """
        nova_connection = self.source_connection.get_nova_connection(self.source_region_name)
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.resource_manager.detach_all_volume(nova_connection))
        except:
            raise

    @asyncio.coroutine
    def _retrieve_information(self):
        nova_connection = self.source_connection.get_nova_connection(self._source_region_name)
        cinder_connection = self.source_connection.get_cinder_connection(self._source_region_name)
        yield from self.resource_manager.retrieve_information(nova_connection, cinder_connection, self.instance_id)

    def _make_migration(self):
        nova_connection_source = self.source_connection.get_nova_connection(self.source_region_name)
        glance_connection_source = self.source_connection.get_glance_connection(self.source_region_name)
        cinder_connection_source = self.source_connection.get_cinder_connection(self.source_region_name)
        glance_connection_destination = self.destination_connection.get_glance_connection(self.destination_region_name)
        nova_connection_destination = self.destination_connection.get_nova_connection(self.destination_region_name)
        neutron_connection_destination = self.destination_connection.get_neutron_connection(self.destination_region_name)
        cinder_connection_destination = self.destination_connection.get_cinder_connection(self.destination_region_name)
        self.resource_manager.migration(nova_connection_source, glance_connection_source,
                                        glance_connection_destination, nova_connection_destination,
                                        neutron_connection_destination, cinder_connection_source,
                                        cinder_connection_destination)
