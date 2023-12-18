#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR

DEST=/opt/firefox-standard-the-latest
mkdir -p $DEST

chmod +x *.py
chmod +x *.sh

cp -avxu * $DEST

cp firefox-standard-the-latest.png /usr/share/pixmaps
cp firefox-standard-the-latest.desktop /usr/share/applications
cp firefox-standard-the-latest-cron.sh /etc/cron.hourly
