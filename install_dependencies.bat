@echo off
setlocal enabledelayedexpansion

set "PYTHON_DIR=resources\python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

echo Verificando dependencias...
if not exist "%PYTHON_EXE%" (
    echo Python portable no encontrado, descargando...
    powershell -Command "Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python.zip'"
    powershell -Command "Expand-Archive -Path 'python.zip' -DestinationPath '%PYTHON_DIR%'"
    del python.zip
)

echo Instalando pip...
curl -L https://bootstrap.pypa.io/get-pip.py -o get-pip.py
"%PYTHON_EXE%" get-pip.py
del get-pip.py

echo Instalando paquetes requeridos...
"%PYTHON_EXE%" -m pip install cryptography ollama qrcode[pil]

echo Descargando modelo de IA...
"%PYTHON_DIR%\Scripts\ollama.exe" pull deepseek-coder:6.7b

echo Instalación completada!
pause