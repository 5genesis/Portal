#!/usr/bin/env bash

python=$1
version="$($python --version)"
if [ ${?} -eq 0 ]; then
    echo "Using $version"
    
    echo "Creating Virtualenv..."
    $python -m venv ./venv

    echo "Installing requirements..."
    source ./venv/bin/activate
    pip install -r ./requirements.txt
    pip install waitress

    echo "Initializing database..."
    flask db upgrade

    deactivate
else
    echo "Could not obtain Python version, please check script parameter. Aborting."
fi
