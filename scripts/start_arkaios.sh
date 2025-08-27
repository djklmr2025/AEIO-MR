#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Detectar comando de Python
PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

# Activa venv
if [ -f ".venv/bin/activate" ]; then
  . .venv/bin/activate
else
  echo "No existe .venv; creando..."
  $PYTHON_CMD -m venv .venv
  . .venv/bin/activate
  pip install -U pip
  if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install flask python-dotenv; fi
fi

# ... (resto del código igual)

# Lanza el server (bind 0.0.0.0 para Codespaces)
exec $PYTHON_CMD "$SERVER_FILE"