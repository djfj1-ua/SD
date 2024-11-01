@echo off
echo Construyendo la imagen
docker build -t customer .

if "%1"=="" (
    echo Uso: start.bat [ID_Cliente] [IP del broker Kafka]
    goto :eof
)

if "%2"=="" (
    echo Uso: start.bat [ID_Cliente] [IP del broker Kafka]
    goto :eof
)

set BROKER_IP=%~2

:: Reescribimos .env
echo BROKER_IP=%BROKER_IP% > .env
echo BROKER_PORT=9092 >> .env

echo Ejecutando Customer
docker run --env-file .env -e CUSTOMER_ID=%1 -it customer