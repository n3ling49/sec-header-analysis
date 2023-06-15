#!/bin/bash

result=$( docker images -q secheader )

if [[ -z "$result" ]]; then
    echo "*******************************"
    echo "* Building secheader image... *"
    echo "*******************************"
    docker build -t secheader .
fi

echo "**********************************"
echo "* Running secheader container... *"
echo "**********************************"
docker run secheader