#!/bin/bash

REPOSITORY=$1
V=`./getLatestReleaseNumber.sh $REPOSITORY`
DIRNAME="$2"
OUTFILE="/tmp/gimx-web_$V.tar.gz"

curl -s "https://api.github.com/repos/$REPOSITORY/releases/latest" | grep tarball_url | tr -d ',' | cut -d':' -f2- | tr -d \" | wget -O $OUTFILE -qi -
curl -s "https://api.github.com/repos/$REPOSITORY/releases/latest" | grep "browser_download_url.*.deb" | cut -d':' -f2- | tr -d \" | wget -O $DIRNAME/gimx.deb -qi -
mkdir $DIRNAME
#tar zxvf $OUTFILE -C $DIRNAME/
rm $OUTFILE
