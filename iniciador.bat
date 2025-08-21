@echo off
setlocal enableextensions
title Lanzador Arkaios - Selector (venv)
chcp 65001 >nul
color 0A

REM ----- RUTAS -----
set PROY=C:\arkaios\ui_local
set VENV=%PROY%\.venv
set PY=%VENV%\Scripts\python.exe

set SRV_OPENAI=%PROY%\server.py
set SRV_GEMINI=%PROY%\server_gemini.py
set SRV_OLLAMA=%PROY%\server_ollama_ui.py
set OLLAMA_EXE=C:\Users\djklm\AppData\Local\Programs\Ollama\ollama.exe

REM Todos escuchan en 8000
set PORT=8000
set URL=http://127.0.0.1:%PORT%/

cd /d "%~dp0"

call :ensure_venv || goto :end
call :ensure_deps

:menu
cls
echo ===================================
echo     Lanzador Arkaios - Selector
echo ===================================
echo 1. OpenAI
echo 2. Gemini
echo 3. Ollama
echo 4. Salir
echo.
choice /C 1234 /N /M "Elige una opcion [1-4]: "
if errorlevel 4 goto end
if errorlevel 3 goto run_ollama
if errorlevel 2 goto run_gemini
if errorlevel 1 goto run_openai
goto menu

:run_openai
call :check_file "%SRV_OPENAI%" || goto menu
echo Iniciando servidor (OpenAI) en venv...
start "Arkaios - OpenAI" cmd /k "\"%PY%\" \"%SRV_OPENAI%\""
call :wait_ready "%URL%"
call :start_app
goto menu

:run_gemini
call :check_file "%SRV_GEMINI%" || goto menu
echo Iniciando servidor (Gemini) en venv...
start "Arkaios - Gemini" cmd /k "\"%PY%\" \"%SRV_GEMINI%\""
call :wait_ready "%URL%"
call :start_app
goto menu

:run_ollama
call :check_file "%SRV_OLLAMA%" || goto menu
if exist "%OLLAMA_EXE%" (
  echo Iniciando Ollama...
  start "Ollama" "%OLLAMA_EXE%" serve
) else (
  echo [ADVERTENCIA] No se encontro: %OLLAMA_EXE%
  echo Ajusta la ruta si lo tienes en otro lugar.
)
echo Iniciando servidor (Ollama) en venv...
start "Arkaios - Ollama" cmd /k "\"%PY%\" \"%SRV_OLLAMA%\""
call :wait_ready "%URL%"
call :start_app
goto menu

:ensure_venv
if exist "%PY%" (
  echo [OK] venv detectado en "%VENV%"
  exit /b 0
)
echo Creando venv en "%VENV%" ...
py -m venv "%VENV%"
if not exist "%PY%" (
  echo [ERROR] No se pudo crear el venv. Verifica que Python este instalado (py).
  pause
  exit /b 1
)
echo Actualizando pip...
"%PY%" -m pip install -U pip >nul
exit /b 0

:ensure_deps
echo Instalando dependencias basicas en venv (una sola vez)...
REM Flask + requests para los servers; openai y python-dotenv por si usas server.py original
"%PY%" -m pip install --disable-pip-version-check -q flask requests python-dotenv openai
REM Si usas FastAPI en tu nube.html de pruebas, descomenta:
REM "%PY%" -m pip install -q fastapi uvicorn python-multipart
exit /b 0

:wait_ready
set "_URL=%~1"
echo Esperando a que el backend responda en %_URL% ...
for /l %%i in (1,1,60) do (
  powershell -NoProfile -Command ^
    "$p='SilentlyContinue';$ProgressPreference=$p;try{$r=Invoke-WebRequest -UseBasicParsing -Uri '%_URL%' -TimeoutSec 2;if($r.StatusCode -ge 200 -and $r.StatusCode -lt 500){exit 0}}catch{};exit 1"
  if not errorlevel 1 (
    echo Backend listo.
    goto :wr_done
  )
  ping 127.0.0.1 -n 2 >nul
)
echo [ADVERTENCIA] No se pudo verificar el backend (continuo de todos modos)...
:wr_done
exit /b 0

echo.
pause
exit /b 0
)

:check_file
if not exist %~1 (
  echo [ERROR] Falta el archivo: %~1
  pause
  exit /b 1
)
exit /b 0

:end
echo Saliendo...
timeout /t 1 >nul
exit /b
