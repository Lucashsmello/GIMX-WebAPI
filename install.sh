#!/bin/bash

#sudo apt install python3 python3-pip python3-dev -y && python3 -m pip install -r requirements.txt
#python3 -m pip install -U pip wheel setuptools

LOCK_FILE=/tmp/lock-gimxwebapi-install.lock
SERVICE_NAME=gimx-web.service
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME
PORT=51916
V=`cat version.txt`
ARCH=`dpkg --print-architecture`

function usage() {
	printf "Usage:\
\t$0
\t$0 --help
\t$0 --uninstall
\t$0 [-p <PORT>] [--install-dir <DIRECTORY>] [--dont-install-gimx] [--mod <MOD>]\n"
}

function quit() {
	rm $LOCK_FILE
	exit $1
}

if [ "$#" -eq 1 ]; then
	if [ "$1" == "--help" ]; then
		usage
		exit
	fi
fi

if [ -f "$LOCK_FILE" ]; then
	echo "$LOCK_FILE exists"
	exit 2
fi
touch $LOCK_FILE

if [ "$#" -eq 1 ]; then
	if [ "$1" == "--uninstall" ]; then
		echo "Uninstalling..."
		if [ -f $SERVICE_PATH ]; then
			systemctl stop $SERVICE_NAME
			systemctl disable $SERVICE_NAME
			rm $SERVICE_PATH
		fi
		quit 0
	fi
fi

INSTALL_DIR=""
INSTALL_GIMX=y
MOD=""

while [[ $# -gt 0 ]]
do
	key="$1"

	case $key in
		-p|--port)
			PORT="$2"
			shift # past argument
			shift # past value
		;;
		--install-dir)
			INSTALL_DIR="$2/$V"
			shift # past argument
			shift # past value
		;;
		--dont-install-gimx)
			INSTALL_GIMX=n
			shift
		;;
		--mod)
			MOD=$2
			shift
			shift
		;;
		*)	# unknown option
			echo "Invalid option: $1"
			quit 1
		;;
	esac
done

if [ -z "$INSTALL_DIR" ]; then
	INSTALL_DIR="`pwd`"
	EXEC_DIR="$INSTALL_DIR/src"
else
	mkdir -p "$INSTALL_DIR"
	EXEC_DIR="`realpath $INSTALL_DIR`/src"
	if ! cp -r src auto_updater version.txt $INSTALL_DIR/.; then
		quit 3
	fi
fi
mkdir -p "$INSTALL_DIR/log"


echo "EXEC_DIR: $EXEC_DIR"

SERVICE_CONTENT="\
[Unit]
Description=GIMX Web Service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$EXEC_DIR
ExecStart=/usr/bin/env python3 webAPI.py -p $PORT

[Install]
WantedBy=multi-user.target"

if systemctl is-active --quiet $SERVICE_NAME; then
	sleep 2
fi

if [ "$INSTALL_GIMX" = "y" ]; then
	curV=`gimx --version | cut -d" " -f2`
	for f in build/gimx*$ARCH*$MOD*.deb; do
		if [ -e "$f" ]; then
			newV=`echo "$f" | cut -d"_" -f2 | cut -d"-" -f1`
			if [ "$curV" = "$newV" ]; then
				echo "GIMX $curV already installed."
				break
			else
				#systemctl stop $SERVICE_NAME
				echo "installing $f"
				if ! dpkg -i $f; then
					echo "Error in installing gimx."
					quit 4
				fi
			fi
		else
			echo "Error in installing gimx. No deb file found."
			quit 4
		fi
		break
	done
fi

printf "$SERVICE_CONTENT" > $SERVICE_PATH
systemctl daemon-reload
rm $LOCK_FILE
echo "Installation successful!"
systemctl enable $SERVICE_NAME && systemctl restart $SERVICE_NAME
