#!/bin/bash

#apt install python python-pip
#pip install -r requirements.txt

LOCK_FILE=/tmp/lock-gimxwebapi-install.lock

if [ -f "$LOCK_FILE" ]; then
	echo "$LOCK_FILE exists"
	exit 2
fi

touch $LOCK_FILE

SERVICE_NAME=gimx-web.service
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME
PORT=80
V=`cat version.txt`

function usage() {
	printf "Usage:\
\t$0\n\
\t$0 -p <PORT>\n\
\t$0 --help\n\
\t$0 --uninstall\n 
\t$0 --install-dir DIRECTORY\n"
}

function quit() {
	rm $LOCK_FILE
	exit $1
}

START_SERVICE="y"
if [ "$#" -eq 1 ]; then
	if [ "$1" == "--help" ]; then
		usage
		quit 0
	fi

	if [ "$1" == "--uninstall" ]; then
		echo "Uninstalling..."
		if [ -f $SERVICE_PATH ]; then
			systemctl stop $SERVICE_NAME
			systemctl disable $SERVICE_NAME
			rm $SERVICE_PATH
		fi
		quit 0
	fi

	if [ "$1" == "-p" ]; then
		PORT=$2
	else
		echo "Invalid argument: $1"
		usage
		quit 1
	fi
fi

if [ "$#" -eq 2 ]; then
	if [ "$1" == "--install-dir" ]; then
		INSTALL_DIR=$2/$V
		mkdir -p $INSTALL_DIR
		EXEC_DIR=`realpath $INSTALL_DIR`/src
		if ! cp -r src auto_updater version.txt $INSTALL_DIR/.; then
			quit 3
		fi
	else
		echo "Invalid argument: $1"
		usage
		quit 1
	fi
else
	EXEC_DIR=`pwd`/src
fi



echo "EXEC_DIR: $EXEC_DIR"
SERVICE_CONTENT="[Unit]
Description=GIMX Web Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$EXEC_DIR
ExecStart=/usr/bin/env python webAPI.py -p $PORT

[Install]
WantedBy=multi-user.target"


if systemctl is-active --quiet $SERVICE_NAME; then
	sleep 2
	for f in build/gimx*.deb; do
		if [ -e "$f" ]; then
			#systemctl stop $SERVICE_NAME
			echo "installing $f"
			dpkg -i $f
		else
			echo "Error in installing gimx"
		fi
		break
	done
fi

printf "$SERVICE_CONTENT" > $SERVICE_PATH
systemctl daemon-reload
rm $LOCK_FILE
systemctl enable $SERVICE_NAME && systemctl restart $SERVICE_NAME
