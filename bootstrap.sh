#!/bin/bash

# Script to bootstrap the installation of required components the 5GENESIS portal, 
# automating the manual instructions at
# https://gitlab.fokus.fraunhofer.de/5genesis/portal/blob/develop/README.md

set -e  # Exit on error

# CONFIGURATION

# Auto-detect user-name, used for setting paths in config files at end of this script.
# Note that username is forced to vagrant if running in the vagrant environment
USER=$(whoami)  
HOME=$(echo $(getent passwd $USER )| cut -d : -f 6)

# Detect if we are executing in a vagrant environment
if [ -d /vagrant ]; then
    VAGRANT=1
    cd /vagrant
    USER=vagrant
    HOME=/home/vagrant
else
    VAGRANT=0
    echo "Warning. You are about to install 5GENESIS system components on your system."
    echo "It will upgrade system softare, set python3.7 as the default python version,"
    echo "and remove your default apache configuration, among other things (inspect this script)"
    echo ""
    echo "Please press ctrl-c to abort or type yes + enter to continue"
    read confirmation
    if [ "${confirmation}" != "yes" ]; then
        echo "Not confirmed. Exiting."
        exit 1
    else
      echo "Confirmed. Proceeding."
    fi
fi


if [ -z ${PKGINSTALLED+x} ]; then
  export PKGINSTALLED=1  
 
  # Install required packages
  sudo apt-get -y update
  sudo apt-get -y install python3.7 python3.7-venv python3.7-dev python3-pip
  sudo apt-get -y install supervisor nginx git

  # set python3.7 as the system default - reverted - buggy as py3.7 is not module-complete w py3.6
  #rm /usr/bin/python3
  #ln -s /usr/bin/python3.7 /usr/bin/python3

  python3.7 -m pip install pip

else

  # Reload script in order to be able to use pip3.7 (the PKGINSTALLED flag will
  # take care of script flow aftex exec'd
  exec bash $0

fi

# Setup the python virtualenvironment


python3.7 -m pip install virtualenv
python3.7 -m virtualenv "$HOME/venv"

. "$HOME/venv/bin/activate"

python3.7 -m pip install -r requirements.txt
python3.7 -m pip install gunicorn


# Copy config files + adapt paths
cwd=$(pwd)

sudo cp Vagrant/supervisor-template.conf /etc/supervisor/conf.d/5gportal.conf
sed -ie "s#__INSTALLDIRECTORY__#${cwd}#" /etc/supervisor/conf.d/5gportal.conf
sed -ie "s#__USER__#${USER}#" /etc/supervisor/conf.d/5gportal.conf
sudo supervisorctl reload

# Configure nginx (no ssl, see Vagrant/nginx_ssl-template.conf for an https configuration example)
sudo rm /etc/nginx/sites-enabled/default
sudo cp Vagrant/nginx-template.conf /etc/nginx/sites-enabled/5gportal
sed -ie "s#__INSTALLDIRECTORY__#${cwd}#" /etc/nginx/sites-enabled/5gportal
sudo service nginx reload

