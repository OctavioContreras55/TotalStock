@echo off
title TotalStock - Test de Funcionamiento
echo 🧪 Probando ejecutable corregido...
echo.
echo 📁 Ubicación del ejecutable:
echo %~dp0dist\TotalStock\TotalStock.exe
echo.
echo ⏱️ Iniciando aplicación...
echo.

cd /d "%~dp0dist\TotalStock"
if exist "TotalStock.exe" (
    echo ✅ Ejecutable encontrado
    echo 🚀 Iniciando TotalStock...
    echo.
    start "" "TotalStock.exe"
    echo ⏳ Aplicación iniciada. Si no aparece, revisa si hay errores.
) else (
    echo ❌ No se encontró el ejecutable en la ubicación esperada
    echo 📁 Verifica que esté en: dist\TotalStock\TotalStock.exe
)

echo.
echo 📋 Si la aplicación no inicia correctamente:
echo 1. Verifica que todas las DLLs estén incluidas
echo 2. Ejecuta desde la línea de comandos para ver errores
echo 3. Contacta para soporte técnico
echo.
pause
