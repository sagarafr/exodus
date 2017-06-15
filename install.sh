#!/usr/bin/env bash

sudo apt update && sudo apt install python3-pip python3-venv
sudo -H pip3 install --upgrade pip3 setuptools
sudo -H pip3 install -r requirements.txt
