@echo off
title Arkaios Financial System

echo Verificando instalación de Python...
python -c "import sqlite3" 2>nul
if %errorlevel% neq 0 (
   echo ERROR: Python no está instalado correctamente
   echo Instalando Python portable...
   powershell -Command "Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python.zip'"
   powershell -Command "Expand-Archive -Path 'python.zip' -DestinationPath 'resources\python'"
   del python.zip
)

echo Optimizando entorno para CPU...
set OLLAMA_NUM_GPU=0
set OLLAMA_NUM_THREADS=4

echo Iniciando servidor Ollama...
start "" ollama serve

echo Esperando 15 segundos para inicialización...
timeout /t 15 /nobreak >nul

echo Iniciando IA Unsensured...
start "" server_local.py

if %errorlevel% neq 0 (
   echo ERROR: La IA Unsensured no inicio como correspondia
   pause
   exit /b
)

echo Iniciando interfaz principal...
start "" ...