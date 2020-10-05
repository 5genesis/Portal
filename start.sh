#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    port="5000"
else
    port=$1
fi

echo Starting Portal on port $port
source ./venv/bin/activate
waitress-serve --listen=*:$port portal:app
deactivate
