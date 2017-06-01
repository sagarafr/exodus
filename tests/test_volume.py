from getpass import getpass
from connections.nova_connection import NovaConnection
from connections.cinder_connection import CinderConnection
from connections.glance_connection import GlanceConnection
from utils.detach_volume import detach_all_volumes
from utils.attach_a_volume import attach_volumes
from migration.snapshot import make_volume_snapshot
from migration.snapshot import make_hard_disk_snapshot
from migration.migration import migration
from datetime import datetime


def info_volume():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "version": "2",
             "region_name": "GRA3"}
    ovh_cinder_connection = CinderConnection(**creds)
    for volume in ["73aebee4-7dd3-40e0-a806-66786711ec20", "cb85bf50-9c0e-4988-ac85-f26079605a76"]:
        print(ovh_cinder_connection.connection.volumes.get(volume).to_dict())
        ovh_cinder_connection.connection.volumes.upload_to_image(volume, True, "image " + volume, "bare", "qcow2")


def migrate():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username:" ),
             "password": getpass(),
             "version": "2",
             "region_name": "GRA3"}
    ovh_cinder_connection = CinderConnection(**creds)
    creds_src = {"authentication": ovh_cinder_connection.authentication,
                 "version": 2,
                 "region_name": "GRA3"}
    ovh_glance_src_connection = GlanceConnection(**creds_src)
    creds_dest = {"authentication": ovh_cinder_connection.authentication,
                  "version": 2,
                  "region_name": "BHS3"}
    ovh_glance_dest_connection = GlanceConnection(**creds_dest)
    creds_nova = {"auth_url": "https://auth.cloud.ovh.net/v3",
                  "user_domain_name": "default",
                  "username": input("Username: "),
                  "password": getpass(),
                  "version": 2,
                  "region_name": "GRA3"}
    ovh_nova_connection = NovaConnection(**creds_nova)
    for volume in ["73aebee4-7dd3-40e0-a806-66786711ec20", "cb85bf50-9c0e-4988-ac85-f26079605a76"]:
        snapshot_name = volume + datetime.now().isoformat()
        make_hard_disk_snapshot(ovh_cinder_connection, ovh_glance_src_connection, ovh_nova_connection, volume, snapshot_name)
        migration(ovh_glance_src_connection, ovh_glance_dest_connection, snapshot_name, snapshot_name)


def test_volume():
    creds = {"auth_url": "https://auth.cloud.ovh.net/v3",
             "user_domain_name": "default",
             "username": input("Username: "),
             "password": getpass(),
             "version": "2",
             "region_name": "GRA3"}
    ovh_nova_connection = NovaConnection(**creds)
    creds_cinder = {"authentication": ovh_nova_connection.authentication,
                    "version": "2",
                    "region_name": "GRA3"}
    ovh_cinder_connection = CinderConnection(**creds_cinder)
    detach_all_volumes(ovh_nova_connection, "b0e90412-89eb-42ca-b411-c73badd5cb35")
    for volume_id in ["73aebee4-7dd3-40e0-a806-66786711ec20", "cb85bf50-9c0e-4988-ac85-f26079605a76"]:
        make_volume_snapshot(ovh_cinder_connection, volume_id, "snap " + volume_id)
    attach_volumes(ovh_nova_connection, "b0e90412-89eb-42ca-b411-c73badd5cb35", ["73aebee4-7dd3-40e0-a806-66786711ec20", "cb85bf50-9c0e-4988-ac85-f26079605a76"])
    for volume in ovh_nova_connection.connection.volumes.get_server_volumes("b0e90412-89eb-42ca-b411-c73badd5cb35"):
        print(volume.to_dict())


if __name__ == '__main__':
    migrate()
    # info_volume()
    # test_volume()
