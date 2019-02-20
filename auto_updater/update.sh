#!/bin/bash

REPOSITORY='Lucashsmello/GIMX-WebAPI'
RELEASE_DIR='releases'
if [ ! -d "$RELEASE_DIR" ]; then
	mkdir $RELEASE_DIR
fi
V=`./getLatestReleaseNumber.sh $REPOSITORY`
./download.sh $REPOSITORY "$RELEASE_DIR/$V"
cd $RELEASE_DIR/$V && ./install_linux.sh

