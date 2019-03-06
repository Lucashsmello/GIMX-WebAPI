#!/bin/bash

if [ "$#" -eq 0 ]; then
	echo "Must specify new installation directory"
	exit 1
fi

if [ "$#" -eq 1 ]; then
	INSTALL_DIR=$1
	REPOSITORY='Lucashsmello/GIMX-WebAPI'
	V=`curl --silent "https://api.github.com/repos/$REPOSITORY/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")'`
	INSTALLER_PATH="$RELEASE_DIR/installer.tar.gz"
	./download.sh $REPOSITORY $INSTALLER_PATH
fi

if [ "$#" -eq 2 ]; then
	INSTALLER_PATH=$1
	INSTALL_DIR=$2
fi

INSTALL_DIR=`realpath $INSTALL_DIR`

echo "INSTALLER_PATH: $INSTALLER_PATH"
echo "INSTALL_DIR: $INSTALL_DIR"

$OPTS=""
if [ -f "$HOME/.dont-install-gimx" ]; then
	$OPTS="--dont-install-gimx"
fi

#V=`tar zxvf $INSTALLER_PATH version.txt -O`
mkdir -p /tmp/gimx-web-installer
tar zxvf $INSTALLER_PATH -C /tmp/gimx-web-installer && cd /tmp/gimx-web-installer && ./install.sh --install-dir $INSTALL_DIR $OPTS &

