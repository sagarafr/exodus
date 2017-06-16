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
* You can be drive by the command `connection` with this following step :
  * Enter password, because it's token is in alpha
  * Enter your authentication url
  * Enter your OpenStack username
  * Enter your OpenStack password
  * Enter your OpenStack tenant id

## Make an instance migration between 2 regions

To migrate an instance between 2 regions you **must** have 1 OpenStack credentials.

* Source openrc file with the following command : `source openrc.sh`
* Launch the shell with the following command : `python3 main.py`
* You have already a connection if the credentials in openrc file are valid and
see "You are connected to URL as USERNAME" in the first line
* If you don't have a connection you must create a connection with the `connection` command

## Make an instance migration between 2 project

To migrate an instance between 2 projects you **must** have 2 OpenStack credentials.

* Source openrc file with the following command : `source openrc.sh`
* Launch the shell with the following command : `python3 main.py`
* You have already a connection if the credentials in openrc file are valid and
see "You are connected to URL as USERNAME" in the first line
*  Basically, to make a migration between 2 projects you have 2 connection.
The first one is the source connection, where is your instance. The second
one is the destination connection, where you want to migrate your instance.
You can create a new connection with the following command : `connection`
* If the connection is successful you must see : "You are connected to URL as USERNAME"
* Now, all connections are setup, you can launch the following command : `
migration URL_SOURCE USER_SOURCE REGION_NAME_SOURCE URL_DESTINATION USER_DESTINATION
REGION_NAME_DESTINATION INSTANCE_NAME`

**Caution** :
* If you have in the region name source multiple instance with the
same name, the migration will take the first instance.
* You can use the instance ID but it's in beta mode

*Information* :
* If you have some space in the instance name you can escape it with '\\' symbol before the space
* If you don't have enough places in your project, the `migration` command
will make his best and tell you what it have do.
