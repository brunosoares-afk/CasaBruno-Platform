#!/bin/bash

ADB="/usr/local/bin/adb"

$ADB start-server

sleep 2

$ADB connect 192.168.20.248:5555

$ADB connect 192.168.20.99:5555

sleep 2

$ADB devices
