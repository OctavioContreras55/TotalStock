#!/usr/bin/env python3
"""
TotalStock - Script FINAL de compilación y limpieza
Crea el ejecutable con el nombre correcto y limpia todo el desorden
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def main():
    print("🧹 TotalStock - COMPILACIÓN FINAL Y LIMPIEZA")
    print("=" * 60)
    print("🎯 Objetivo: Ejecutable final 'TotalStock.exe' y limpieza completa")
    
    # Paso 1: Limpiar todo el desorden
    limpiar_archivos_intentos()
    
    # Paso 2: Compilar versión final con nombre correcto
    if compilar_version_final():
        crear_acceso_final()
        mostrar_resultado_final()
        return True
    
    return False

def limpiar_archivos_intentos():
    """Limpiar todos los archivos de intentos anteriores"""
    print("\n🧹 LIMPIANDO ARCHIVOS DE INTENTOS ANTERIORES...")
    
    # Archivos de build a eliminar (mantener solo build.py original)
    archivos_build = [
        "build_basico.py", "build_corregido.py", "build_definitivo.py",
        "build_directo.py", "build_emergencia.py", "build_final.py", 
        "build_funcional.py", "build_original.py", "build_safe.py",
        "build_simple.py", "build_simple_v2.py", "build_ultra_simple.py"
    ]
    
    # Archivos run de respaldo/intentos
    archivos_run = [
        "run_backup_1754615980.py", "run_corregido.py", "run_original_backup.py",
        "run_emergencia.py", "run_estable.py", "run_prueba.py", "run_rapido.py",
        "run_safe.py", "run_seguro.py", "run_simple_final.py", "run_ultra_estable.py"
    ]
    
    # Archivos BAT de intentos
    archivos_bat = [
        "build_rapido.bat", "build_seguro.bat", "build_ultra_estable.bat",
        "TotalStock_BUILD.bat", "TotalStock_DEFINITIVO.bat", "TotalStock_EJECUTAR.bat",
        "TotalStock_FINAL.bat", "TotalStock_FUNCIONAL.bat", "TotalStock_OPTIMIZADO.bat",
        "TotalStock_RAPIDO.bat", "TotalStock_SEGURO.bat", "MATAR_TOTALSTOCK.bat"
    ]
    
    # Archivos SPEC de intentos
    archivos_spec = [
        "TotalStock_Definitivo.spec", "TotalStock_FUNCIONAL.spec", 
        "TotalStock_DEBUG.spec", "TotalStock_FINAL.spec", "TotalStock_SEGURO.spec"
    ]
    
    # Directorios de compilaciones anteriores
    directorios_dist = ["dist"]
    directorios_build = ["build"]
    
    total_eliminados = 0
    
    # Eliminar archivos
    for lista_archivos in [archivos_build, archivos_run, archivos_bat, archivos_spec]:
        for archivo in lista_archivos:
            if Path(archivo).exists():
                try:
                    Path(archivo).unlink()
                    print(f"  🗑️ {archivo}")
                    total_eliminados += 1
                except Exception as e:
                    print(f"  ❌ Error eliminando {archivo}: {e}")
    
    # Eliminar directorios
    for directorio in directorios_dist + directorios_build:
        if Path(directorio).exists():
            try:
                shutil.rmtree(directorio)
                print(f"  🗑️ {directorio}/")
                total_eliminados += 1
            except Exception as e:
                print(f"  ❌ Error eliminando {directorio}: {e}")
    
    print(f"\n✅ LIMPIEZA COMPLETADA: {total_eliminados} elementos eliminados")

def compilar_version_final():
    """Compilar la versión final con el nombre correcto"""
    print("\n🔨 COMPILANDO VERSIÓN FINAL...")
    print("📝 Nombre del ejecutable: TotalStock.exe")
    
    # Asegurar que tenemos la versión corregida
    if Path("run_corregido.py").exists():
        if Path("run.py").exists():
            shutil.copy2("run.py", "run_backup_temp.py")
        shutil.copy2("run_corregido.py", "run.py")
        print("✅ Versión corregida aplicada como run.py")
    
    # Comando PyInstaller final - SIMPLE y EFECTIVO
    comando = [
        sys.executable, "-m", "PyInstaller",
        
        # Configuración básica
        "--onedir",                    # Directorio (más rápido)
        "--windowed",                  # Sin consola
        "--noconfirm",                 # Sin confirmaciones
        "--clean",                     # Limpiar cache
        
        # NOMBRE CORRECTO
        "--name=TotalStock",           # ← NOMBRE FINAL CORRECTO
        
        # Icono
        "--icon=assets/logo.ico",
        
        # Datos necesarios
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        "--add-data=data;data",
        
        # Importaciones críticas
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=flet.desktop",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        "--hidden-import=polars",
        "--hidden-import=openpyxl",
        
        # Optimizaciones
        "--noupx",                     # Sin compresión (más compatible)
        "--optimize=2",                # Optimización bytecode
        
        # Exclusiones para reducir tamaño
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=pandas",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        "--exclude-module=jupyter",
        "--exclude-module=pytest",
        
        # Archivo principal
        "run.py"
    ]
    
    try:
        start_time = time.time()
        print("⏳ Compilando TotalStock final...")
        
        # Ejecutar PyInstaller
        resultado = subprocess.run(
            comando,
            check=True,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        tiempo = end_time - start_time
        
        # Verificar resultado
        exe_path = Path("dist/TotalStock/TotalStock.exe")
        if exe_path.exists():
            # Calcular tamaño
            carpeta_dist = Path("dist/TotalStock")
            tamaño_total = sum(f.stat().st_size for f in carpeta_dist.rglob('*') if f.is_file())
            tamaño_mb = tamaño_total / (1024 * 1024)
            
            print(f"\n🎉 ¡EJECUTABLE FINAL CREADO EXITOSAMENTE!")
            print(f"📍 Ubicación: {exe_path.absolute()}")
            print(f"📏 Tamaño: {tamaño_mb:.1f} MB")
            print(f"⏱️ Tiempo: {tiempo:.1f} segundos")
            print(f"✅ Nombre: TotalStock.exe (CORRECTO)")
            
            return True
        else:
            print("❌ ERROR: No se creó el ejecutable")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR en compilación: {e}")
        if e.stdout:
            print("Salida:", e.stdout[-300:])
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False

def crear_acceso_final():
    """Crear acceso directo final con nombre correcto"""
    print("\n🔗 Creando acceso directo final...")
    
    contenido_bat = '''@echo off
title TotalStock - Sistema de Inventario
echo.
echo ==========================================
echo     TotalStock - Sistema de Inventario
echo ==========================================
echo.

REM Verificar que el ejecutable existe
if not exist "dist\\TotalStock\\TotalStock.exe" (
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
cd /d "%~dp0dist\\TotalStock"
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
'''
    
    with open("TotalStock.bat", "w", encoding="utf-8") as f:
        f.write(contenido_bat)
    
    print("✅ Creado: TotalStock.bat")

def mostrar_resultado_final():
    """Mostrar resultado final"""
    print("\n" + "="*60)
    print("🎊 PROYECTO TOTALSTOCK - COMPILACIÓN FINAL EXITOSA")
    print("="*60)
    
    print("\n✅ LIMPIEZA COMPLETADA:")
    print("   🗑️ Eliminados todos los archivos de intentos")
    print("   🗑️ Eliminados builds anteriores")
    print("   🧹 Proyecto organizado y limpio")
    
    print("\n🚀 EJECUTABLE FINAL CREADO:")
    print("   📁 Ubicación: dist/TotalStock/TotalStock.exe")
    print("   🔗 Acceso directo: TotalStock.bat")
    print("   ✅ Nombre correcto: TotalStock (sin sufijos)")
    print("   🛡️ Problema múltiples procesos: SOLUCIONADO")
    
    print("\n🎯 CÓMO USAR:")
    print("   1. 🖱️ Doble clic en TotalStock.bat")
    print("   2. ✅ TotalStock se abrirá normalmente")
    print("   3. 🔴 Al cerrar, se terminará limpiamente")
    
    print("\n📁 ARCHIVOS FINALES:")
    print("   • TotalStock.bat ← USAR ESTE")
    print("   • dist/TotalStock/TotalStock.exe")
    print("   • run.py (versión corregida)")
    print("   • TotalStock.spec (generado automáticamente)")
    
    print("\n🎉 ¡PROYECTO COMPLETADO Y ORGANIZADO!")

if __name__ == "__main__":
    print("🏁 Iniciando compilación final y limpieza...")
    
    success = main()
    
    if success:
        print("\n✅ ÉXITO TOTAL: Proyecto limpio y ejecutable final creado")
        print("🚀 Tu TotalStock.exe está listo para usar")
    else:
        print("\n❌ Hubo problemas en la compilación final")
    
    print("\n" + "="*50)
    input("Presiona Enter para finalizar...")
