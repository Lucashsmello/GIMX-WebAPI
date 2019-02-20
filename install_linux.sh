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


START_SERVICE="y"
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
	fi

	if [ "$1" == "--dont-start" ]; then
		START_SERVICE="n"
	else
		echo "Invalid argument: $1"
		usage
		exit 1
	fi
fi


EXEC_DIR=`pwd`/src
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

printf "$SERVICE_CONTENT" > $SERVICE_PATH
if [ "$START_SERVICE" == "y" ]; then
	./start_service.sh
fi
