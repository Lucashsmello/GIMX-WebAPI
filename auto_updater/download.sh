#!/bin/bash

REPOSITORY=$1
V=`./getLatestReleaseNumber.sh $REPOSITORY`
DIRNAME="$2"
OUTFILE="/tmp/gimx-web_$V.tar.gz"

curl -s "https://api.github.com/repos/$REPOSITORY/releases/latest" | grep tarball_url | tr -d ',' | cut -d':' -f2- | tr -d \" | wget -O $OUTFILE -qi -
mkdir $DIRNAME
tar zxvf $OUTFILE -C $DIRNAME/
rm $OUTFILE
