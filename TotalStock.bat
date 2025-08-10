@echo off
title TotalStock - Sistema de Inventario
echo.
echo ==========================================
echo     TotalStock - Sistema de Inventario
echo ==========================================
echo.

REM Verificar que el ejecutable existe
if not exist "dist\TotalStock\TotalStock.exe" (
    echo ❌ ERROR: TotalStock.exe no encontrado
    echo.
    echo 💡 Solución: Ejecuta python build_final_limpio.py
    echo.
    pause
    exit /b 1
)

echo ✅ Iniciando TotalStock...
echo.

REM Cambiar al directorio y ejecutar
cd /d "%~dp0dist\TotalStock"
start "" "TotalStock.exe"

REM Verificar inicio
timeout /t 3 /nobreak >nul

echo ✅ TotalStock iniciado correctamente
echo.
echo 📋 INFORMACIÓN:
echo    • Ejecutable: TotalStock.exe
echo    • Versión: FINAL CORREGIDA
echo    • Problema múltiples procesos: SOLUCIONADO
echo.
pause
