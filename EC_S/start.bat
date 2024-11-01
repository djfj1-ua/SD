@echo off
echo Creando imagen Sensor
docker build -t sensor .
echo Ejecutando Sensor
docker run --env-file .env -it sensor
