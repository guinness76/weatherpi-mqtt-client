#!/bin/bash
now=`date +%m%d%Y_%H%M`
newZip=`echo weatherpi-mqtt-client-$now.zip`
exclusions="-x weatherpi-mqtt-client/ignition-gateway/\* -x weatherpi-mqtt-client/.git/\*"

(cd .. && zip -r $newZip weatherpi-mqtt-client -x "weatherpi-mqtt-client/ignition-gateway**" -x "weatherpi-mqtt-client/.git**")