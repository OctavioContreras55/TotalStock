#!/usr/bin/env python3
"""
Script de compilación completa - Todas las características para producción
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_completo():
    """Crear ejecutable completo con todas las características para producción"""
    
    print("[PACKAGE] TotalStock - Compilación Completa (Producción)")
    print("=" * 60)
    print("[INICIO] Versión completa con todas las optimizaciones...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Limpiar build anterior
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"[LIMPIEZA] Limpiando: {carpeta}/")
    
    print("\n[CONFIG] Creando versión completa para producción...")
    
    # Comando PyInstaller completo con todas las características
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Archivo único para distribución
        "--windowed",
        "--name=TotalStock_Produccion",
        "--noconfirm",
        
        # Datos completos
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        "--add-data=data;data",
        
        # Importaciones completas
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=flet.auth",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        "--hidden-import=google.cloud.firestore",
        "--hidden-import=polars",
        "--hidden-import=polars",
        "--hidden-import=openpyxl",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=asyncio",
        
        # Recopilar módulos completos para máxima compatibilidad
        "--collect-all=flet",
        "--collect-all=firebase_admin",
        "--collect-all=google.cloud",
        
        # Copiar metadatos
        "--copy-metadata=flet",
        "--copy-metadata=firebase_admin",
        "--copy-metadata=google-cloud-firestore",
        
        # Optimizaciones para producción
        "--strip",  # Remover símbolos de debug
        "--optimize=2",  # Optimización máxima
        
        "run.py"
    ]
    
    # Agregar icono si existe
    if os.path.exists("assets/logo.ico"):
        comando.extend(["--icon", "assets/logo.ico"])
    
    try:
        print("[ESPERA] Construyendo ejecutable completo (puede tomar varios minutos)...")
        print("[IDEA] Esta versión incluye todas las dependencias y optimizaciones")
        
        resultado = subprocess.run(comando, check=True)
        
        exe_path = Path("dist/TotalStock_Produccion.exe")
        
        if exe_path.exists():
            # Calcular tamaño
            tamaño_mb = exe_path.stat().st_size / (1024 * 1024)
            
            print(f"\n[OK] ¡Compilación completa exitosa!")
            print(f"[FOLDER] Ubicación: {exe_path.absolute()}")
            print(f"[CHART] Tamaño: {tamaño_mb:.1f} MB")
            
            print(f"\n[INICIO] CARACTERÍSTICAS DE PRODUCCIÓN:")
            print("   • [OK] Archivo único portátil")
            print("   • [OK] Todas las dependencias incluidas")
            print("   • [OK] Optimizado para distribución")
            print("   • [OK] Sin dependencias externas")
            print("   • [OK] Máxima compatibilidad")
            
            print(f"\n[LISTA] INSTRUCCIONES DE DISTRIBUCIÓN:")
            print("[INICIO] Listo para distribuir:")
            print("   1. Copia el archivo TotalStock_Produccion.exe")
            print("   2. Envía o instala en cualquier PC Windows")
            print("   3. Ejecuta directamente - no necesita instalación")
            print("   4. Compatible con Windows 7, 8, 10, 11")
            
            # Crear acceso rápido
            crear_acceso_produccion(exe_path)
            
            return True
        else:
            print("[ERROR] Ejecutable no encontrado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en PyInstaller: {e}")
        return False

def crear_acceso_produccion(exe_path):
    """Crear acceso rápido para la versión de producción"""
    try:
        bat_content = f'''@echo off
title TotalStock - Versión de Producción
echo [INICIO] Iniciando TotalStock (Versión de Producción)...
echo [PACKAGE] Ejecutable: {exe_path.absolute()}
echo.
"{exe_path.absolute()}"
'''
        
        with open("TotalStock_PRODUCCION.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        print("[OK] Acceso rápido creado: TotalStock_PRODUCCION.bat")
        
    except Exception as e:
        print(f"[WARN]  Error creando acceso rápido: {e}")

if __name__ == "__main__":
    success = build_completo()
    
    if success:
        print("\n🎊 ¡Compilación completa lista!")
        print("[PACKAGE] Perfecta para distribución y producción")
        print("[STAR] Incluye todas las características y optimizaciones")
    else:
        print("\n[ERROR] Hubo problemas en la compilación.")
    
    input("\nPresiona Enter para continuar...")
