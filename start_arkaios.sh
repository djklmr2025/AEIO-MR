#!/bin/bash

# ARKAIOS - Linux Shell Launcher
# Ejecutar: ./start_arkaios.sh

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes de éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar advertencias
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar errores
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para mostrar información
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner de inicio
echo -e "${GREEN}"
echo "========================================"
echo "    ARKAIOS - Laboratorio Puter + ChatGPT"
echo "========================================"
echo -e "${NC}"

# Verificar si estamos en el directorio correcto
check_files() {
    info "Verificando archivos necesarios..."
    
    if [ ! -f "server_arkaios.py" ]; then
        error "No se encuentra server_arkaios.py"
        echo "Ejecuta este script en la misma carpeta que server_arkaios.py"
        exit 1
    fi
    
    if [ ! -f "arkaios.html" ]; then
        error "No se encuentra arkaios.html"
        echo "Ejecuta este script en la misma carpeta que arkaios.html"
        exit 1
    fi
    
    success "Todos los archivos necesarios encontrados"
}

# Verificar e instalar Python
check_python() {
    info "Verificando Python..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python3 no está instalado"
        echo "Instala Python3 con:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "  Fedora: sudo dnf install python3 python3-pip"
        echo "  Arch: sudo pacman -S python python-pip"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    success "Python $PYTHON_VERSION detectado"
}

# Verificar e instalar pip
check_pip() {
    info "Verificando pip..."
    
    if ! command -v pip3 &> /dev/null; then
        warning "pip3 no encontrado, intentando instalar..."
        
        # Intentar instalar pip
        if command -v apt &> /dev/null; then
            sudo apt install python3-pip -y
        elif command -v dnf &> /dev/null; then
            sudo dnf install python3-pip -y
        elif command -v pacman &> /dev/null; then
            sudo pacman -S python-pip --noconfirm
        else
            error "No se pudo instalar pip automáticamente"
            echo "Instala pip manualmente para tu distribución"
            exit 1
        fi
    fi
    
    success "pip3 detectado"
}

# Instalar dependencias
install_dependencies() {
    info "Verificando dependencias..."
    
    # Verificar Flask
    if ! python3 -c "import flask" 2>/dev/null; then
        warning "Flask no instalado, instalando..."
        pip3 install flask
    fi
    
    # Verificar requests
    if ! python3 -c "import requests" 2>/dev/null; then
        warning "Requests no instalado, instalando..."
        pip3 install requests
    fi
    
    success "Dependencias verificadas"
}

# Función principal
main() {
    # Verificar requisitos
    check_files
    check_python
    check_pip
    install_dependencies
    
    echo ""
    info "Iniciando servidor ARKAIOS..."
    echo -e "${YELLOW}🌐 Servidor: http://127.0.0.1:5000${NC}"
    echo -e "${YELLOW}⏹️  Presiona Ctrl+C para detener el servidor${NC}"
    echo -e "${YELLOW}📁 Directorio: $(pwd)${NC}"
    echo ""
    
    # Ejecutar el servidor
    python3 server_arkaios.py
    
    # Verificar si el servidor se cerró con error
    if [ $? -ne 0 ]; then
        error "El servidor se detuvo debido a un error"
        echo "Verifica que el puerto 5000 no esté en uso:"
        echo "  lsof -i :5000"
        echo "O mata el proceso:"
        echo "  pkill -f server_arkaios.py"
    fi
}

# Manejar señal de interrupción (Ctrl+C)
trap 'echo ""; warning "Servidor detenido por el usuario"; exit 0' INT

# Ejecutar función principal
main