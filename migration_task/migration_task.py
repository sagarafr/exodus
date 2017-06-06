from datetime import datetime

from connections.nova_connection import NovaConnection
from connections.cinder_connection import CinderConnection
from utils.detach_volume import detach_all_volumes
from utils.attach_a_volume import attach_a_volume
from migration.snapshot import make_hard_disk_snapshot
from migration.snapshot import make_snapshot_from_uuid
from migration.migration import migration
from migration.launch_instance import launch_instance
from utils.get_from_image import get_container_format
from utils.get_from_image import get_disk_format
from utils.get_ids import get_ovh_default_nics
from utils.get_ids import get_server_id_from_nova
from utils.get_ids import get_flavor_id
from utils.find_flavors import find_flavor_name
from time import sleep


class MigrationTask:
    def __init__(self, **kwargs):
        try:
            self._src_connection = kwargs['src_connection']
            self._dest_connection = kwargs['dest_connection']
        except Exception as exception_message:
            print(exception_message)
            raise
        self._hard_disk_information = []
        self._hard_disk_snapshot_name = []
        self._hard_disk_created = []
        self._server_information = None
        self._server_snapshot_name = None
        self._server_id = None
        self._src_region_name = None
        self._dest_region_name = None
        self._link_hard_disk_snap_to_hard_disk = {}
        self._instance = None

    @property
    def src_connection(self):
        return self._src_connection

    @property
    def dest_connection(self):
        return self._dest_connection

    @src_connection.setter
    def src_connection(self, value):
        self._src_connection = value

    @dest_connection.setter
    def dest_connection(self, value):
        self._dest_connection = value

    @property
    def hard_disk_information(self):
        return self._hard_disk_information

    @property
    def server_information(self):
        return self._server_information

    @server_information.setter
    def server_information(self, value):
        self._server_information = value

    @property
    def src_region_name(self):
        return self._src_region_name

    @property
    def dest_region_name(self):
        return self._dest_region_name

    def prepare_migration(self, instance_id: str, region_name: str):
        try:
            self._src_region_name = region_name
            self._server_id = instance_id
            nova_connection = self.src_connection.get_nova_connection(region_name)
            cinder_connection = self.src_connection.get_cinder_connection(region_name)
            self.prepare_storage_migration_with_instance_id(nova_connection, cinder_connection, instance_id)
            self.server_information = nova_connection.connection.servers.get(instance_id).to_dict()
        except:
            raise
        # detach_all_volumes(nova_connection, instance_id)

    def prepare_storage_migration_with_instance_id(self, nova_connection: NovaConnection,
                                                   cinder_connection: CinderConnection, instance_id: str):
        try:
            for volume in nova_connection.connection.volumes.get_server_volumes(instance_id):
                id_volume = volume.to_dict()['id']
                self.hard_disk_information.append(cinder_connection.connection.volumes.get(id_volume).to_dict())
        except:
            raise

    # TODO make this on thread mode : 1 thread = snap + migration + instance (make this async)
    def migration_to(self, region_name: str):
        self._dest_region_name = region_name
        self.make_snapshots()
        # nova_connection = self.src_connection.get_nova_connection(region_name)
        # attach_volumes(nova_connection, self._server_id, [str(hard_disk['id']) for hard_disk in self.hard_disk_information])
        self.make_migrations()
        self.make_instances()

    def make_snapshots(self):
        self.make_hard_disk_snapshot()
        self.make_instance_snapshot()

    def make_hard_disk_snapshot(self):
        cinder_connection = self.src_connection.get_cinder_connection(self.src_region_name)
        glance_connection = self.src_connection.get_glance_connection(self.src_region_name)
        nova_connection = self.src_connection.get_nova_connection(self.src_region_name)
        print(self.hard_disk_information)
        for hard_disk in self.hard_disk_information:
            id_hard_disk = hard_disk['id']
            snapshot_name = id_hard_disk + datetime.now().isoformat() + '_volume'
            self._link_hard_disk_snap_to_hard_disk[snapshot_name] = id_hard_disk
            self._hard_disk_snapshot_name.append(snapshot_name)
            make_hard_disk_snapshot(cinder_connection, glance_connection, nova_connection, hard_disk['id'], snapshot_name)

    def make_instance_snapshot(self):
        nova_connection = self.src_connection.get_nova_connection(self.src_region_name)
        self._server_snapshot_name = self._server_id + datetime.now().isoformat() + '_instance'
        make_snapshot_from_uuid(nova_connection, self._server_id, self._server_snapshot_name)

    def make_migrations(self):
        print("make_migration")
        glance_src_connection = self.src_connection.get_glance_connection(self.src_region_name)
        glance_dest_connection = self.dest_connection.get_glance_connection(self.dest_region_name)

        for snapshot_hard_disk in self._hard_disk_snapshot_name:
            print("snap hard disk", snapshot_hard_disk)
            migration(glance_src_connection, glance_dest_connection, snapshot_hard_disk, snapshot_hard_disk)
            print("end migration hard_disk", snapshot_hard_disk)

        disk_format = get_disk_format(glance_src_connection, self._server_snapshot_name)
        disk_format = "qcow2" if len(disk_format) == 0 else disk_format[0]
        container_format = get_container_format(glance_src_connection, self._server_snapshot_name)
        container_format = "bare" if len(container_format) == 0 else container_format[0]

        print("begin migration instance", self._server_snapshot_name)
        migration(glance_src_connection, glance_dest_connection, self._server_snapshot_name,
                  self._server_snapshot_name, disk_format, container_format)
        print("end migration instance", self._server_snapshot_name)

    def make_instances(self):
        cinder_connection = self.dest_connection.get_cinder_connection(self.dest_region_name)
        nova_connection_src = self.src_connection.get_nova_connection(self.src_region_name)
        nova_connection_dest = self.dest_connection.get_nova_connection(self.dest_region_name)
        neutron_connection = self.dest_connection.get_neutron_connection(self.dest_region_name)

        print("begin instance", self._server_information)
        flavor_id = self._server_information['flavor']['id']
        flavor_name = find_flavor_name(nova_connection_src, flavor_id)[0]
        print("flavor name", flavor_name)
        instance = launch_instance(nova_connection_dest, self._server_information['name'], self._server_snapshot_name,
                                   flavor_name, get_ovh_default_nics(neutron_connection))
        print("end instance")
        self._instance = instance.to_dict()

        for hard in self._hard_disk_created:
            print(hard)
            try:
                print(hard.to_dict())
            except Exception as exception_message:
                print(exception_message)

        for snapshot_hard_disk in self._hard_disk_snapshot_name:
            print("begin creation", snapshot_hard_disk)
            print(self._link_hard_disk_snap_to_hard_disk[snapshot_hard_disk])
            id_hard_disk = self._link_hard_disk_snap_to_hard_disk[snapshot_hard_disk]
            size = None
            for hard_disk in self._hard_disk_information:
                print(hard_disk)
                if hard_disk['id'] == id_hard_disk:
                    size = hard_disk['size']
            print(size)
            hard_disk = cinder_connection.connection.volumes.create(size, imageRef=snapshot_hard_disk)
            print("end creation", snapshot_hard_disk)
            self._hard_disk_created.append(hard_disk.to_dict())

        for hard in self._hard_disk_created:
            print(hard)

        print(instance)
        try:
            print(instance.to_dict())
        except Exception as exception_message:
            print(exception_message)
        self.attach_hard_disk_to_instance()

    def attach_hard_disk_to_instance(self):
        nova_connection = self.dest_connection.get_nova_connection(self.dest_region_name)
        cinder_connection = self.dest_connection.get_cinder_connection(self.dest_region_name)
        status = nova_connection.connection.servers.get(self._instance['id']).to_dict()['status']
        while status != 'ACTIVE':
            status = nova_connection.connection.servers.get(self._instance['id']).to_dict()['status']
            print("[{}]".format(status))
            if status != 'ACTIVE':
                sleep(2)
        while len(self._hard_disk_created) != 0:
            print(self._hard_disk_created)
            for cpt_hard_disk in range(0, len(self._hard_disk_created)):
                hard_disk = self._hard_disk_created[cpt_hard_disk]
                disk_information = cinder_connection.connection.volumes.get(hard_disk['id']).to_dict()
                print(disk_information)
                status = disk_information['status']
                if status == 'available':
                    attach_a_volume(nova_connection, self._instance['id'], hard_disk['id'])
                    self._hard_disk_created.pop(cpt_hard_disk)
                    break
            sleep(2)
