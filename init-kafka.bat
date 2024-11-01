@echo off
setlocal

if "%1"=="" (
    echo Introduce la direccion IP [sin puerto]
    goto :eof
)

set BROKER_IP=%~1

echo Iniciando docker-compose con BROKER_IP=%BROKER_IP%
docker compose up

endlocal