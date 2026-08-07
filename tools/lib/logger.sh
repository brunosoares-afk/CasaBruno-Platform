#!/usr/bin/env bash

LOG_DIR="/opt/CasaBruno-Platform/logs"
mkdir -p "$LOG_DIR"

log(){

echo "$(date '+%F %T') $1" >> "$LOG_DIR/cbos.log"

}
