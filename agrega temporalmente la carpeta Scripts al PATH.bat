@echo off
REM Carpeta Scripts de tu app
set "SCRIPTS_PATH=C:\arkaios\miapp\dist\ArkaiosApp-win32-x64\resources\Scripts"

REM Agregar temporalmente al PATH
set "PATH=%SCRIPTS_PATH%;%PATH%"

REM Ruta al ejecutable principal de tu app
set "APP_PATH=C:\arkaios\miapp\dist\ArkaiosApp-win32-x64\ArkaiosApp.exe"

REM Mensaje informativo
echo Ejecutando Arkaios con PATH temporal...
echo.

REM Ejecutar la app
"%APP_PATH%"

REM Pausa para ver mensajes si es necesario
pause
