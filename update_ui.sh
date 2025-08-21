#!/bin/bash
set -e

# Ruta del zip (ajusta si lo subes a otra carpeta)
ZIPFILE="ui_local.zip"

# Asegúrate de que existe
if [ ! -f "$ZIPFILE" ]; then
  echo "❌ No se encontró $ZIPFILE en la raíz"
  exit 1
fi

# Extrae el zip en carpeta temporal
TMPDIR=$(mktemp -d)
unzip -o "$ZIPFILE" -d "$TMPDIR"

# Copia su contenido encima del repo actual
cp -rT "$TMPDIR/ui_local" .

# Limpieza
rm -rf "$TMPDIR"

echo "✅ Archivos de ui_local.zip sobrescritos en el repo actual"
