# INSTALL

## Shell
For ubuntu version 16.04.2 LTS or Debian, simply launch ./install.sh
For the other :
* Update all your system packages
* Install python3, python3-pip and python3-venv
* Update pip and setuptools with the following command : `sudo -H pip3 install pip setuptools --upgrade`
* Install missing package with the following command : `sudo -H pip3 install -r requirements.txt`

### Virtualenv install
```
    pyvenv-3.4 exodus
    source bin/activate
    pip3 install pip setuptools --upgrade
    pip3 install -r requirements.txt
    git clone ssh://git@stash.ovh.net:7999/cloud/exodus.git
```
