#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 037"
echo "========================================"
echo

echo "Instalando Service Dispatcher..."

mkdir -p "$ROOT/backend/app/fred/dispatcher"

touch "$ROOT/backend/app/fred/dispatcher/__init__.py"

cat > "$ROOT/backend/app/fred/dispatcher/dispatcher.py" << 'PY'
class Dispatcher:

    def dispatch(self,service):

        services={
            "LightService":"Executando LightService",
            "WeatherService":"Executando WeatherService",
            "DockerService":"Executando DockerService",
            "NetworkService":"Executando NetworkService",
            "HomeAssistantService":"Executando HomeAssistantService",
            "FallbackService":"Nenhum serviço encontrado"
        }

        return services.get(service,"Serviço inválido")

dispatcher=Dispatcher()
PY

cat > "$ROOT/backend/app/fred/dispatcher/test.py" << 'PY'
from dispatcher import dispatcher

print(dispatcher.dispatch("LightService"))
print(dispatcher.dispatch("WeatherService"))
print(dispatcher.dispatch("DockerService"))
print(dispatcher.dispatch("NetworkService"))
print(dispatcher.dispatch("HomeAssistantService"))
print(dispatcher.dispatch("FallbackService"))
PY

echo
echo "[OK] Service Dispatcher instalado."
echo
