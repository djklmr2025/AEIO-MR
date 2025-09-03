#!/bin/bash

# ARKAIOS - macOS Launcher
cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "   ARKAIOS - Laboratorio Puter + ChatGPT"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 no está instalado"
    echo "Instala Python desde: https://www.python.org/downloads/"
    echo "O con Homebrew: brew install python"
    open "https://www.python.org/downloads/"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ ERROR: pip3 no está instalado"
    echo "Instala pip: python3 -m ensurepip --upgrade"
    exit 1
fi

# Verificar archivos
if [ ! -f "server_arkaios.py" ]; then
    echo "❌ ERROR: server_arkaios.py no encontrado"
    exit 1
fi

if [ ! -f "arkaios.html" ]; then
    echo "❌ ERROR: arkaios.html no encontrado"
    exit 1
fi

# Instalar dependencias si faltan
echo "🔍 Verificando dependencias..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando Flask..."
    pip3 install flask
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando Requests..."
    pip3 install requests
fi

echo ""
echo "🚀 Iniciando servidor ARKAIOS..."
echo "🌐 Servidor: http://127.0.0.1:5000"
echo "⏹️  Presiona Ctrl+C para detener"
echo ""

# Ejecutar servidor
python3 server_arkaios.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: No se pudo iniciar el servidor"
    echo "Verifica los archivos y dependencias"
    exit 1
fi