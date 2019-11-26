#!/bin/sh

# Script to bootstrap the installation of required components the 5GENESIS portal, 
# automating the manual instructions at
# https://gitlab.fokus.fraunhofer.de/5genesis/portal/blob/develop/README.md

set -e  # Exit on error

if [ -z ${PKGINSTALLED+x} ]; then
  export PKGINSTALLED=1
 
  # Install required packages
  sudo apt-get -y update
  sudo apt-get -y install python3.7 python3.7-venv python3.7-dev python3-pip
  sudo apt-get -y install supervisor nginx git
  python3.7 -m pip install pip
else
  # Reload script in order to be able to use pip3.7 (the PKGINSTALLED flag will take care of script flow)
  bash $0
fi



# Install requirements. Please consider using virtualenv when installing on a shared machine.
# FIXME - implement venv
#

cd /vagrant

# FIXME - handle non-vagrant cases. Maybe test for path existence? 
# i.e.  [ -d /vagrant ] && cd /vagrant
# Check that we are in the correct directory for non-vagrant installations
# i.e. [ -d Vagrant ] && echo "Missing config files in Vagrant directory"


pip3 install -r requirements.txt --user
pip3 install gunicorn --user

# Configure supervisor
sudo cp Vagrant/supervisor.conf /etc/supervisor/conf.d/5gportal.conf
sudo supervisorctl reload

# Configure nginx (no ssl, see Vagrant/nginx_ssl.conf for an https configuration example)
sudo rm /etc/nginx/sites-enabled/default
sudo cp Vagrant/nginx.conf /etc/nginx/sites-enabled/5gportal
sudo service nginx reload

