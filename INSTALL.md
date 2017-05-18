#INSTALL
## Web Site
For the deployment if you have a problem with posgresql you must do this :

`export PYTHONPATH=pwd` with pwd the directory of exodus project

## Shell
For ubuntu version 16.04.2 LTS
* Update all packages in your system with the following command : `sudo apt update && sudo apt upgrade`
* Install pip3 with the following command : `sudo apt install python3-pip`
* Upgrade pip3 with the following command : `sudo -H pip3 install --upgrade pip`
* Install keystoneauth1 with the following command : `sudo -H pip3 install keystoneauth1`
* Install novaclient with the following command : `sudo -H pip3 install python-novaclient`
* Install glanceclient with the following command : `sudo -H pip3 install python-glanceclient`
* Install neutronclient with the following command : `sudo -H pip3 install python-neutronclient`

### Virtualenv install
```
    pyvenv-3.4 exodus
    source bin/activate
    pip3 install --upgrade pip
    pip3 install setuptools --upgrade
    pip3 install keystoneauth1
    pip3 install python-novaclient
    pip3 install python-neutronclient
    pip3 install python-glanceclient
    git clone ssh://git@stash.ovh.net:7999/cloud/exodus.git
```
