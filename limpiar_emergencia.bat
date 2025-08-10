@echo off
echo ===============================================
echo     LIMPIEZA DE EMERGENCIA - TotalStock
echo ===============================================
echo.

echo [1] Terminando procesos TotalStock...
taskkill /f /im TotalStock*.exe 2>nul
taskkill /f /im python.exe 2>nul

echo [2] Limpiando archivos temporales...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul

echo [3] Verificando procesos...
echo Procesos Python activos:
tasklist | findstr /i python 2>nul
if errorlevel 1 echo   - No hay procesos Python ejecutandose

echo.
echo Procesos TotalStock activos:
tasklist | findstr /i totalstock 2>nul
if errorlevel 1 echo   - No hay procesos TotalStock ejecutandose

echo.
echo ===============================================
echo           LIMPIEZA COMPLETADA
echo ===============================================
echo.
echo El sistema esta listo para un nuevo build.
echo.
pause
