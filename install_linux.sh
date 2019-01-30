#!/bin/bash

#apt install python python-pip
#pip install -r requirements.txt

SERVICE_NAME=gimx-web.service
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME
PORT=80

function usage() {
	printf "Usage:\
\t$0\n\
\t$0 -p <PORT>\n\
\t$0 --help\n\
\t$0 --uninstall\n" 
}

if [ "$#" -ge 1 ]; then
	if [ "$1" == "--help" ]; then
		usage
		exit
	fi

	if [ "$1" == "--uninstall" ]; then
		echo "Uninstalling..."
		if [ -f $SERVICE_PATH ]; then
			systemctl stop $SERVICE_NAME
			systemctl disable $SERVICE_NAME
			rm $SERVICE_PATH
		fi
		exit
	fi

	if [ "$1" == "-p" ]; then
		PORT=$2
	else
		echo "Invalid argument: $1"
		usage
		exit 1
	fi
fi


EXEC_PATH=`pwd`/src/webAPI.py
SERVICE_CONTENT="[Unit]
Description=GIMX Web Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/env python $EXEC_PATH -p $PORT

[Install]
WantedBy=multi-user.target"

if [ -f $SERVICE_PATH ]; then
    systemctl stop $SERVICE_NAME
	systemctl disable $SERVICE_NAME
fi

printf "$SERVICE_CONTENT" > $SERVICE_PATH
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

