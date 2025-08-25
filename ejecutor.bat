@echo off
echo Ejecutando start_arkaios.sh...
echo.

REM Verificar si el archivo existe
if not exist "scripts\start_arkaios.sh" (
    echo Error: No se encuentra scripts\start_arkaios.sh
    pause
    exit /b 1
)

REM Ejecutar el script
bash scripts/start_arkaios.sh

REM Pausar para ver el resultado
echo.
echo Ejecucion completada.
pause