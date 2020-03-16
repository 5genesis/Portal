#!/bin/bash

# Script to bootstrap the installation of required components the 5GENESIS portal, 
# automating the manual instructions at
# https://gitlab.fokus.fraunhofer.de/5genesis/elcm/wikis/home
# (formerly https://gitlab.fokus.fraunhofer.de/5genesis/portal/blob/develop/README.md )

set -e  # Exit on error

# CONFIGURATION

# Detect if we are executing in a vagrant environment
if [[ $1 == "vagrant" ]]; then
    cd /vagrant
fi

HOME=$(pwd)
USER=$(whoami)

# Install required packages
export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y update
sudo apt-get -y install python3.7 python3.7-dev python3-pip virtualenv
sudo apt-get -y install supervisor nginx git pwgen

# Setup the python virtual environment
virtualenv --python=python3.7 --always-copy venv
source "$HOME/venv/bin/activate"

pip install -r requirements.txt
pip install gunicorn
flask db upgrade

# Set a secure password on the flask app
SECRET_KEY=$(pwgen 32 1)
sed -ie "s#__REPLACEWITHSECRETKEY__#${SECRET_KEY}#" .flaskenv
sed -ie "s#__REPLACEWITHSECRETKEY__#${SECRET_KEY}#" config.py

sudo cp Vagrant/supervisor-template.conf /etc/supervisor/conf.d/5gportal.conf
sudo sed -ie "s#__INSTALLDIRECTORY__#${HOME}#" /etc/supervisor/conf.d/5gportal.conf
sudo sed -ie "s#__USER__#${USER}#" /etc/supervisor/conf.d/5gportal.conf
sudo supervisorctl reload

# Configure nginx (no ssl, see Vagrant/nginx_ssl-template.conf for an https configuration example)
sudo rm /etc/nginx/sites-enabled/default
sudo cp Vagrant/nginx-template.conf /etc/nginx/sites-enabled/5gportal
sudo sed -ie "s#__INSTALLDIRECTORY__#${HOME}#" /etc/nginx/sites-enabled/5gportal
sudo service nginx reload




