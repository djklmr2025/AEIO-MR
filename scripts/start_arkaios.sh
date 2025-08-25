#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Activa venv
if [ -f ".venv/bin/activate" ]; then
  . .venv/bin/activate
else
  echo "No existe .venv; creando..."
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -U pip
  if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install flask python-dotenv; fi
fi

# Carga .env si existe
if [ -f ".env" ]; then
  echo "Cargando .env…"
  # Exporta todas las variables de CLAVE=valor (ignora comentarios)
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

# Defaults seguros (puedes ajustarlos aquí o en .env)
export ROOT_FORCE_ON="${ROOT_FORCE_ON:-1}"
export ROOT_ALLOW_EXTERNAL="${ROOT_ALLOW_EXTERNAL:-1}"
export MEMORY_DIR="${MEMORY_DIR:-data/memory}"

# Archivo del servidor
SERVER_FILE="${SERVER_FILE:-server_gemini_merged_root.py}"
if [ ! -f "$SERVER_FILE" ]; then
  echo "❌ No se encuentra $SERVER_FILE"
  exit 1
fi

echo "==============================================="
echo " Arkaios • Codespaces"
echo " URL externa se abrirá cuando se reenvíe el puerto 8000"
echo " ROOT_FORCE_ON=$ROOT_FORCE_ON  ROOT_ALLOW_EXTERNAL=$ROOT_ALLOW_EXTERNAL"
echo "==============================================="

# Lanza el server (bind 0.0.0.0 para Codespaces)
exec python "$SERVER_FILE"
