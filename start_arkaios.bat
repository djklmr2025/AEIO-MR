@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    ARKAIOS - Laboratorio Puter + ChatGPT
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar si pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no está instalado
    echo Instala pip o verifica la instalación de Python
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
pip install flask requests >nul 2>&1

echo.
echo Iniciando servidor ARKAIOS...
echo Servidor: http://127.0.0.1:5000
echo Presiona Ctrl+C para detener
echo.

REM Ejecutar el servidor
python server_arkaios.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar el servidor
    echo Verifica que server_arkaios.py esté en la misma carpeta
    pause
)