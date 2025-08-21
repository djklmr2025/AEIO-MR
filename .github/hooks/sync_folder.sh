#!/bin/sh

# Carpeta local que quieres sincronizar
SOURCE_DIR="/path/to/your/local/folder"

# Carpeta dentro del repositorio donde quieres copiar los archivos
DEST_DIR="your/repo/subfolder"

# Repositorio Git
REPO_DIR="/path/to/your/git/repo"

# Navega al directorio del repositorio
cd "$REPO_DIR"

# Copia los archivos
cp -r "$SOURCE_DIR"/* "$DEST_DIR"

# Añade los cambios al staging area
git add "$DEST_DIR"

# Verifica si hay cambios para commitear
if ! git diff --cached --quiet; then
  # Crea un commit con los cambios
  git commit -m "Sincronización automática de la carpeta $SOURCE_DIR"

  # Hace push de los cambios
  git push origin main # o la rama que estés usando
fi
