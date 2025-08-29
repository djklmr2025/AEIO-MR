#!/bin/bash
# install_arkaios.sh - Instalador rápido

echo "🔧 Instalando ARKAIOS..."

# Dar permisos de ejecución
chmod +x start_arkaios.sh

# Verificar si Makefile existe y configurar
if [ -f "Makefile" ]; then
    echo "📦 Configurando Makefile..."
    make check
fi

echo "✅ Instalación completada"
echo "🎯 Para ejecutar: ./start_arkaios.sh"
echo "   o usar: make run"