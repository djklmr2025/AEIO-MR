.PHONY: run install check-python check-deps clean

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m

run: check-python check-deps
	@echo "$(GREEN)🚀 Iniciando servidor ARKAIOS...$(NC)"
	@echo "$(YELLOW)Servidor: http://127.0.0.1:5000$(NC)"
	@echo "$(YELLOW)Presiona Ctrl+C para detener$(NC)"
	@python3 server_arkaios.py

install: check-python
	@echo "$(GREEN)📦 Instalando dependencias...$(NC)"
	@pip3 install flask requests
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

check-python:
	@which python3 > /dev/null 2>&1 || (echo "$(RED)❌ Python3 no está instalado$(NC)"; echo "Instala con: sudo apt install python3 python3-pip"; exit 1)
	@python3 -c "import sys; print('$(GREEN)✅ Python version:', sys.version.split()[0], '$(NC)')"

check-deps:
	@python3 -c "import flask, requests" > /dev/null 2>&1 || (echo "$(YELLOW)⚠️  Dependencias faltantes, instalando...$(NC)"; pip3 install flask requests)

check:
	@echo "$(GREEN)🔍 Verificando archivos...$(NC)"
	@test -f server_arkaios.py || (echo "$(RED)❌ server_arkaios.py no encontrado$(NC)"; exit 1)
	@test -f arkaios.html || (echo "$(RED)❌ arkaios.html no encontrado$(NC)"; exit 1)
	@echo "$(GREEN)✅ Todos los archivos presentes$(NC)"

clean:
	@echo "$(GREEN)🧹 Limpiando archivos temporales...$(NC)"
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

help:
	@echo "$(GREEN)ARKAIOS - Comandos disponibles:$(NC)"
	@echo "  $(YELLOW)make run$(NC)     - Ejecutar servidor"
	@echo "  $(YELLOW)make install$(NC) - Instalar dependencias"
	@echo "  $(YELLOW)make check$(NC)   - Verificar archivos"
	@echo "  $(YELLOW)make clean$(NC)   - Limpiar archivos temporales"
	@echo "  $(YELLOW)make help$(NC)    - Mostrar esta ayuda"