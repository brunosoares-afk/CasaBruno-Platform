#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

source "$ROOT/tools/lib/colors.sh"
source "$ROOT/tools/lib/banner.sh"

banner

echo "Iniciando diagnóstico..."
echo

check(){

    NAME="$1"
    CMD="$2"

    if eval "$CMD" >/dev/null 2>&1
    then
        printf "${GREEN}[ OK ]${RESET} %-30s\n" "$NAME"
    else
        printf "${RED}[FAIL]${RESET} %-30s\n" "$NAME"
    fi

}

echo "=============================="
echo " SISTEMA"
echo "=============================="

check "Git" "git --version"

check "Python3" "python3 --version"

check "PIP" "pip3 --version"

check "Docker" "docker --version"

check "Docker Compose" "docker compose version"

check "NodeJS" "node --version"

check "NPM" "npm --version"

check "Curl" "curl --version"

check "Wget" "wget --version"

check "Tree" "tree --version"

echo

echo "=============================="
echo " CBOS"
echo "=============================="

check "Backend" "[ -d $ROOT/backend ]"

check "Frontend" "[ -d $ROOT/frontend ]"

check "AI" "[ -d $ROOT/ai ]"

check "Docs" "[ -d $ROOT/docs ]"

check "Tools" "[ -d $ROOT/tools ]"

echo

echo "=============================="
echo " REDE"
echo "=============================="

hostname -I

echo

echo "=============================="
echo " MEMÓRIA"
echo "=============================="

free -h

echo

echo "=============================="
echo " DISCO"
echo "=============================="

df -h /

echo

echo "=============================="
echo " CPU"
echo "=============================="

uptime

echo

echo "Diagnóstico concluído."
