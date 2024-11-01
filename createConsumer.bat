@echo off

:: Comprobamos si se han introducido ambos parámetros
if "%1"=="" (
    echo No has introducido ningun parametro de inicio
    goto :eof
)

if "%2"=="" (
    echo No has introducido ningun parametro de fin
    goto :eof
)

:: Mensaje de inicio
echo Creando clientes desde %1 hasta %2

:: Bucle for que comienza en %1 y termina en %2
for /l %%i in (%1,1,%2) do (
   start cmd /k "cd /d .\EC_Customer\Customer && consumer.bat %%i"
)