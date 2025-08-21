@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===============================================
echo       ARKAIOS - GEMINI IA LAUNCHER
echo ===============================================
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

:: Crear carpetas necesarias
echo 📁 Creando carpetas necesarias...
if not exist uploads mkdir uploads
if not exist data mkdir data
if not exist data\memory mkdir data\memory

:: Verificar archivos necesarios
echo 🔍 Verificando archivos necesarios...
set "missing_files="
if not exist "server_gemini.py" set "missing_files=!missing_files! server_gemini.py"
if not exist "magic_gemini.html" set "missing_files=!missing_files! magic_gemini.html"

if not "!missing_files!"=="" (
    echo ERROR: Faltan archivos necesarios:!missing_files!
    echo Por favor asegurate de tener todos los archivos en el mismo directorio.
    pause
    exit /b 1
)

:: Verificar/instalar dependencias
echo 📦 Verificando dependencias de Python...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Instalando Flask...
    pip install flask
)

pip show python-dotenv >nul 2>&1
if errorlevel 1 (
    echo Instalando python-dotenv...
    pip install python-dotenv
)

:: Verificar archivo .env
if not exist ".env" (
    echo 📝 Creando archivo .env de ejemplo...
    echo GEMINI_API_KEY=tu_clave_api_aqui > .env
    echo GEMINI_MODEL=gemini-2.0-flash-exp >> .env
    echo MEMORY_DIR=data/memory >> .env
    echo MEMORY_MAX_TURNS=8 >> .env
    echo MEMORY_SUMMARY_EVERY=6 >> .env
    echo.
    echo ⚠️  IMPORTANTE: Edita el archivo .env y agrega tu clave de API de Gemini
    echo    Puedes obtenerla desde: https://makersuite.google.com/app/apikey
    echo.
    pause
)

:: Verificar si hay una clave API configurada
findstr /i "GEMINI_API_KEY=tu_clave_api_aqui" .env >nul
if not errorlevel 1 (
    echo ⚠️  ADVERTENCIA: La clave de API de Gemini parece no estar configurada
    echo    Edita el archivo .env y reemplaza 'tu_clave_api_aqui' con tu clave real
    echo.
)

echo 🚀 Iniciando servidor Gemini en segundo plano...
start "Arkaios - Gemini Backend" cmd /c "python \"%CD%\server_gemini.py\" & pause"

:: Esperar a que el servidor inicie
echo ⏳ Esperando que el servidor inicie...
ping 127.0.0.1 -n 3 >nul

:: Verificar que el servidor responda
echo 🔍 Verificando conexion al servidor...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  El servidor puede estar iniciando aún. Se abrirá la interfaz en 3 segundos...
    ping 127.0.0.1 -n 4 >nul
)

echo 🌐 Abriendo interfaz web...
start "Arkaios UI" http://127.0.0.1:8000/

echo.
echo ===============================================
echo ✅ Arkaios iniciado correctamente
echo 📍 URL: http://127.0.0.1:8000/
echo 💡 Para detener el servidor, cierra la ventana del backend
echo ===============================================
echo.
echo Presiona cualquier tecla para salir del launcher...
pause >nul

exit /b 0