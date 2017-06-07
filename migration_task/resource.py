from enum import Enum
from json import dumps
from datetime import datetime
import asyncio

from connections.nova_connection import NovaConnection
from connections.cinder_connection import CinderConnection
from connections.glance_connection import GlanceConnection
from connections.neutron_connection import NeutronConnection
from migration.snapshot import make_snapshot_from_uuid
from migration.snapshot import make_hard_disk_snapshot
from migration.migration import migration
from migration.launch_instance import launch_instance
from utils.get_from_image import get_disk_format
from utils.get_from_image import get_container_format
from utils.get_ids import get_ovh_default_nics
from utils.find_flavors import find_flavor_name


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

    def migration(self, nova_connection_source: NovaConnection, glance_connection_source: GlanceConnection,
                  glance_connection_destination: GlanceConnection, nova_connection_destination: NovaConnection,
                  neutron_connection_destination: NeutronConnection, cinder_connection_source: CinderConnection,
                  cinder_connection_destination: CinderConnection):
        try:
            if self.resource_type is ResourceType.Instance:
                self._instance_migration(nova_connection_source, glance_connection_source,
                                         glance_connection_destination, nova_connection_destination,
                                         neutron_connection_destination)
            elif self.resource_type is ResourceType.Storage:
                self._storage_migration(cinder_connection_source, glance_connection_source,
                                        nova_connection_source, glance_connection_destination,
                                        cinder_connection_destination)
        except:
            raise

    def _instance_migration(self, nova_connection_source: NovaConnection, glance_connection_source: GlanceConnection,
                            glance_connection_destination: GlanceConnection, nova_connection_destination: NovaConnection,
                            neutron_connection_destination: NeutronConnection):
        try:
            flavor_name = find_flavor_name(nova_connection_source, self.resource_information['flavor']['id'])[0]
        except:
            raise
        disk_format = "qcow2"
        container_format = "bare"
        try:
            disk_format = get_disk_format(glance_connection_source, self.snapshot_name)[0]
        except IndexError:
            pass
        except:
            raise
        try:
            container_format = get_container_format(glance_connection_source, self.snapshot_name)[0]
        except IndexError:
            pass
        except:
            raise
        print("begin snapshot {} with id {}".format(self.resource_type, self.resource_information['id']))
        self.snapshot_name = self.resource_information['id'] + datetime.now().isoformat() + '_instance'
        make_snapshot_from_uuid(nova_connection_source, self.resource_information['id'], self._snapshot_name)
        print("end snapshot {} with id {}".format(self.resource_type, self.resource_information['id']))

        try:
            print("begin migration {} with id {}".format(self.resource_type, self.resource_information['id']))
            migration(glance_connection_source, glance_connection_destination, self.snapshot_name,
                      self.snapshot_name, disk_format, container_format)
            print("end migration {} with id {}".format(self.resource_type, self.resource_information['id']))
        except:
            raise

        print("begin instance {} with id {}".format(self.resource_type, self.resource_information['id']))
        tmp_resource = launch_instance(nova_connection_destination, self.resource_information['name'],
                                       self.snapshot_name, flavor_name,
                                       get_ovh_default_nics(neutron_connection_destination))
        self.resource_created = tmp_resource.to_dict()
        print("end instance {} with id {}".format(self.resource_type, self.resource_information['id']))

    def _storage_migration(self, cinder_connection_source: CinderConnection, glance_connection_source: GlanceConnection,
                           nova_connection_source: NovaConnection, glance_connection_destination: GlanceConnection,
                           cinder_connection_destination: CinderConnection):
        try:
            size = self.resource_information['size']
        except:
            raise
        print("begin snapshot {} with id {}".format(self.resource_type, self.resource_information['id']))
        self.snapshot_name = self.resource_information['id'] + datetime.now().isoformat() + '_volume'
        make_hard_disk_snapshot(cinder_connection_source, glance_connection_source, nova_connection_source,
                                self.resource_information['id'], self.snapshot_name)
        print("end snapshot {} with id {}".format(self.resource_type, self.resource_information['id']))

        try:
            print("begin migration {} with id {}".format(self.resource_type, self.resource_information['id']))
            migration(glance_connection_source, glance_connection_destination, self.snapshot_name, self.snapshot_name)
            print("end migration {} with id {}".format(self.resource_type, self.resource_information['id']))
        except:
            raise

        print("begin instance {} with id {}".format(self.resource_type, self.resource_information['id']))
        tm_resource = cinder_connection_destination.connection.volumes.create(size, imageRef=self.snapshot_name)
        self.resource_created = tm_resource.to_dict()
        print("end instance {} with id {}".format(self.resource_type, self.resource_information['id']))

    def __str__(self):
        return "resource_information: " + dumps(self.resource_information, indent=4) + '\n' + \
               "snapshot_name: " + self.snapshot_name.__str__() + '\n' + \
               "resource_created: " + dumps(self.resource_created, indent=4) + '\n' + \
               "resource_type: " + self.resource_type.__str__() + '\n'
