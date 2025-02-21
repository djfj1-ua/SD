@echo off
echo Creando imagen Central
docker build -t central .
echo Ejecutando Central
docker run --env-file .env -p 5051:5051 -it central