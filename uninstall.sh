#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

rm -rf /opt/firefox-standard-the-latest
rm -rf /usr/share/pixmaps/firefox-standard-the-latest.png
rm -rf /usr/share/applications/firefox-standard-the-latest.desktop
rm -rf /etc/cron.hourly/firefox-standard-the-latest-cron.sh

