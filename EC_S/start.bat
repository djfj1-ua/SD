@echo off
setlocal

if "%1" == "" (
    echo Introduce el IP [sin puerto] de Digital Engine
    goto :eof
)

echo Creando imagen Sensor
docker build -t sensor .

set ENGINE_IP=%~1

:: Reescribimos .env
echo ENGINE_IP=%ENGINE_IP% > .env
echo ENGINE_PORT=5050 >> .env

echo Ejecutando Sensor
docker run --env-file .env -it sensor
