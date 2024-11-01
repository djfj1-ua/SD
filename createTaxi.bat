@echo off

:: Comprobar si se ha pasado exactamente un parámetro
if "%1"=="" (
    echo Uso: createTaxi.bat [id_taxi] [n_sensores] [central_ip] [central_puerto] [broker_ip]
    goto :eof
)

if "%2"=="" (
    echo Uso: createTaxi.bat [id_taxi] [n_sensores] [central_ip] [central_puerto] [broker_ip]
    goto :eof
)

if "%3"=="" (
    echo Uso: createTaxi.bat [id_taxi] [n_sensores] [central_ip] [central_puerto] [broker_ip]
    goto :eof
)

if "%4"=="" (
    echo Uso: createTaxi.bat [id_taxi] [n_sensores] [central_ip] [central_puerto] [broker_ip]
    goto :eof
)

if "%5"=="" (
    echo Uso: createTaxi.bat [id_taxi] [n_sensores] [central_ip] [central_puerto] [broker_ip]
    goto :eof
)

if not "%6"=="" (
    echo Uso: createTaxi.bat [id_taxi] [n_sensores] [central_ip] [central_puerto] [broker_ip]
    goto :eof
)

start cmd /k "cd EC_DE && start.bat %1 %3 %4 %5"

for /l %%i in (1,1,%2) do (
    start cmd /k "cd EC_S && start.bat 172.17.0.3"
)