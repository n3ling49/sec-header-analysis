#!/bin/bash

image=$( docker images -q secheader )

if [ -z "$image" ] || [ "$1" = "build" ];
then
    echo "*******************************"
    echo "* Building secheader image... *"
    echo "*******************************"
    docker build -t secheader .
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "**********************************"
echo "* Running secheader container... *"
echo "**********************************"
docker run -it -v "$SCRIPT_DIR"/results:/usr/src/app/results secheader