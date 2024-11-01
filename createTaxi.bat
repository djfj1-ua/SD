@echo off

:: Comprobar si se ha pasado exactamente un parámetro
if "%1"=="" (
    echo No has introducido ningun parametro.
    goto :eof
)

if "%2"=="" (
    echo No has introducido el segundo parametro.
    goto :eof
)

if not "%3"=="" (
    echo Has introducido mas de dos parametros.
    goto :eof
)

start cmd /k "cd EC_DE && start.bat %1"
:: Si hay exactamente un parametro, entra aqui
for /l %%i in (1,1,%2) do (
    start cmd /k "cd EC_S && start.bat"
)