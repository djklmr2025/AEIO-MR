Write-Host "Iniciando entorno ARKAIOS..."

# Activar entorno virtual si existe
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activando entorno virtual..."
    & $venvPath
} else {
    Write-Host "No se encontró entorno virtual. Continuando sin él..."
}

# Iniciar el backend ARKAIOS
$backendScript = "server_gemini_merged_root.py"
if (Test-Path $backendScript) {
    Write-Host "Lanzando ARKAIOS (server_gemini_merged_root.py)..."
    python $backendScript
} else {
    Write-Host "server_gemini_merged_root.py no encontrado. ¿Está todo instalado correctamente?"
}

Pause
