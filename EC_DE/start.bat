@echo off
echo Construyendo la imagen
docker build -t engine .
echo Ejecutando Engine
docker run --env-file .env -e TAXI_ID=%1 -it engine