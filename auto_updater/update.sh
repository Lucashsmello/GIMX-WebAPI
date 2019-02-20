#!/bin/bash

REPOSITORY='Lucashsmello/GIMX-WebAPI'
RELEASE_DIR='releases'
if [ -d "$RELEASE_DIR" ]; then
	rm -r "$RELEASE_DIR"
fi
mkdir $RELEASE_DIR
V=`./getLatestReleaseNumber.sh $REPOSITORY`
./download.sh $REPOSITORY "$RELEASE_DIR/$V"
cd $RELEASE_DIR/$V/Lucashsmello* && ./install_linux.sh --dont-start && sleep 2 && ./start_service.sh &

