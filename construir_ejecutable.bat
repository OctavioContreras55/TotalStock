@echo off
title Construccion TotalStock - Ejecutable Completo
color 0A

echo.
echo ===============================================================
echo                 TOTALSTOCK - CONSTRUCCION EJECUTABLE
echo ===============================================================
echo.

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

echo [INFO] Python detectado correctamente
echo.

REM Verificar si pip está disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no está disponible
    pause
    exit /b 1
)

echo [INFO] pip detectado correctamente
echo.

REM Instalar PyInstaller si no está instalado
echo [PASO 1] Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INSTALANDO] PyInstaller no encontrado, instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
    echo [OK] PyInstaller instalado correctamente
) else (
    echo [OK] PyInstaller ya está instalado
)

echo.
echo [PASO 2] Ejecutando script de construcción...
echo.

REM Ejecutar el script de Python
python build_ejecutable_completo.py

if errorlevel 1 (
    echo.
    echo ===============================================================
    echo                      ERROR EN CONSTRUCCION
    echo ===============================================================
    echo.
    echo El proceso de construccion falló. Revisa los errores arriba.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ===============================================================
    echo                    CONSTRUCCION EXITOSA
    echo ===============================================================
    echo.
    echo El ejecutable se ha creado en: dist\TotalStock.exe
    echo.
    echo INSTRUCCIONES PARA DISTRIBUIR:
    echo 1. Copia UNICAMENTE el archivo dist\TotalStock.exe
    echo 2. Este archivo ya contiene todas las dependencias de Python
    echo 3. No necesita que Python esté instalado en el PC destino
    echo 4. Funciona en Windows 10/11 de 64 bits
    echo.
    echo ¿Quieres abrir la carpeta dist?
    pause
    explorer dist
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
