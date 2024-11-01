@echo off
setlocal
echo Construyendo la imagen
docker build -t engine .

set CENTRAL_IP=%~2
set CENTRAL_PORT=%~3
set BROKER_IP=%~4

:: Reescribimos .env
echo CENTRAL_IP=%CENTRAL_IP% > .env
echo CENTRAL_PORT=%CENTRAL_PORT% >> .env
echo BROKER_IP=%BROKER_IP% >> .env
echo BROKER_PORT=9092 >> .env

echo Ejecutando Engine
docker run --env-file .env -e TAXI_ID=%1 -it engine