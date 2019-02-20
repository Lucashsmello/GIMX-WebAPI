#!/bin/bash

SERVICE_NAME=gimx-web.service
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME

if [ -f $SERVICE_PATH ]; then
	systemctl daemon-reload
fi
systemctl restart $SERVICE_NAME && systemctl enable $SERVICE_NAME
