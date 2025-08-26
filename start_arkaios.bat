@echo off
chcp 65001 >nul
title Arkaios AI Server Launcher
color 0B

echo ========================================
echo      ARKAIOS AI SERVER LAUNCHER
echo ========================================
echo.

:menu
echo Selecciona el servidor a iniciar:
echo.
echo   [1] Gemini Server (magic.html)
echo   [2] Claude Server (index.html) 
echo   [3] Salir
echo.
set /p choice="Elige una opción (1-3): "

if "%choice%"=="1" goto gemini
if "%choice%"=="2" goto claude
if "%choice%"=="3" goto exit
echo Opción inválida. Por favor elige 1, 2 o 3.
echo.
goto menu

:gemini
echo.
echo Iniciando servidor Gemini...
echo Servidor: server_gemini_merged_root.py
echo Frontend: magic.html
echo Puerto: 8000
echo URL: http://127.0.0.1:8000
echo.
timeout /t 2 /nobreak >nul

start "" "http://127.0.0.1:8000"
python server_gemini_merged_root.py

pause
goto menu

:claude
echo.
echo Iniciando servidor Claude...
echo Servidor: server_claude_puter.py  
echo Frontend: index.html (con Puter.js)
echo Puerto: 8000
echo URL: http://127.0.0.1:8000
echo.
timeout /t 2 /nobreak >nul

start "" "http://127.0.0.1:8000"
python server_claude_puter.py

pause
goto menu

:exit
echo.
echo Saliendo del launcher...
timeout /t 2 /nobreak >nul
exit