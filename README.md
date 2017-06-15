# README

Code name : exodus

Tools to migrate inter OVH region for OpenStack

# Shell

First, read INSTALL.md file to install all missing package.

To launch the shell write the following command : `python3 main.py`

# Shell usage

## Shell command

A basic exodus shell client. The commands available are :
* `bye / exit` : exit the console
* `connection` : ask credentials and make a connection to a openstack project
* `change_connection` : change the current connection
* `list_connection` : list all different connections
* `catalog` : print all information of the current connection
* `migration` : make a migration of one instance between to 2 regions or 2 projects
* `list_flavor` : list flavors of the current connection
* `list_region` : list regions of the current connection
* `list_instance` : list all instances of the current connection

## Make a connection

To make a connection you have 2 basic way :
* You can source an file content all OpenStack credentials with the following
command : `source openrc.sh`
* You can be drive by the command `connection`

## Make an instance migration between 2 project

To migrate an instance between 2 projects you **must** have OpenStack credentials.

This shell can detect OpenStack authentication from the environment. First
of all, download the openrc.sh file corresponding to the region of the instance
to migrate. Then source this openrc.sh file.

After that you can launch the shell with the following command : `python3 main.py`

If your credentials are correct you have something like that appear : `Connected with You are connected to URL as USER`
with URL the authentication URL and USER the OpenStack user.

If you don't have this line at the beginning of the shell, don't worried,
you can make a connection with the command `connection`
Then the shell ask you some information like if you want a OpenStack
token authentication (beta) or a password authentication.

For the password authentication, you **must** have :
* The authentication url
* OpenStack Username
* User domain name (keep this by default by pressing enter)
* OpenStack Password
* Tenant id, if your authentication is in v2

After that you can use the command `migration` to make the migration.
To use the migration command do like this :
`migration URL_SRC USER_SRC REGION_SRC URL_DEST USER_DEST REGION_DEST INSTANCE_NAME`
with in order the authentication url source, the OpenStack user source,
the region name source, the authentication url destination, the OpenStack
user destination, the region name destination and the instance name to migrate

**Caution** :
* If you have in the region name source multiple instance with the
same name, the migration will take the first instance.
* You can use the instance ID but it's in beta mode

*Information* :
If you have some space in the instance name you can escape it with '\\' symbol before the space
