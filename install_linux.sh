#!/bin/bash

#apt install python python-pip
#pip install -r requirements.txt

SERVICE_NAME=gimx-web.service
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME

if [ "$1" == "--uninstall" ]; then
	echo "Uninstalling..."
	if [ -f $SERVICE_PATH ]; then
		systemctl stop $SERVICE_NAME
		systemctl disable $SERVICE_NAME
		rm $SERVICE_PATH
	fi
	exit
fi

EXEC_PATH=`pwd`/src/main.py
SERVICE_CONTENT="[Unit]
Description=GIMX Web Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/env python3 $EXEC_PATH

[Install]
WantedBy=multi-user.target"

if [ -f $SERVICE_PATH ]; then
    systemctl stop $SERVICE_NAME
	systemctl disable $SERVICE_NAME
fi

printf "$SERVICE_CONTENT" > $SERVICE_PATH
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

