#!/usr/bin/env python3
"""
Script de compilación básica - Versión rápida para desarrollo
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_basico():
    """Crear ejecutable básico rápido para pruebas"""
    
    print("[CONFIG] TotalStock - Compilación Básica (Rápida)")
    print("=" * 50)
    print("[INICIO] Optimizado para desarrollo y pruebas rápidas...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Limpiar build anterior
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"[LIMPIEZA] Limpiando: {carpeta}/")
    
    print("\n[RAPIDO] Creando versión básica...")
    
    # Comando PyInstaller básico
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name=TotalStock_Basico",
        "--noconfirm",
        
        # Solo datos esenciales
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        
        # Importaciones mínimas
        "--hidden-import=flet",
        "--hidden-import=firebase_admin",
        "--hidden-import=polars",
        "--hidden-import=polars",
        
        # Exclusiones para velocidad
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        
        # Sin compresión para velocidad
        "--noupx",
        
        "run.py"
    ]
    
    # Agregar icono si existe
    if os.path.exists("assets/logo.ico"):
        comando.extend(["--icon", "assets/logo.ico"])
    
    try:
        print("[ESPERA] Construyendo ejecutable básico...")
        resultado = subprocess.run(comando, check=True)
        
        exe_path = Path("dist/TotalStock_Basico/TotalStock_Basico.exe")
        
        if exe_path.exists():
            # Calcular tamaño
            carpeta_dist = Path("dist/TotalStock_Basico")
            tamaño_total = sum(f.stat().st_size for f in carpeta_dist.rglob('*') if f.is_file())
            tamaño_mb = tamaño_total / (1024 * 1024)
            
            print(f"\n[OK] ¡Compilación básica completada!")
            print(f"[FOLDER] Ubicación: {exe_path.absolute()}")
            print(f"[CHART] Tamaño: {tamaño_mb:.1f} MB")
            
            print(f"\n[LISTA] INSTRUCCIONES DE USO:")
            print("🏃‍♂️ Para ejecutar:")
            print(f"   cd {carpeta_dist}")
            print("   ./TotalStock_Basico.exe")
            
            return True
        else:
            print("[ERROR] Ejecutable no encontrado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en PyInstaller: {e}")
        return False

if __name__ == "__main__":
    success = build_basico()
    
    if success:
        print("\n[SUCCESS] ¡Compilación básica lista!")
        print("[IDEA] Ideal para pruebas rápidas de desarrollo")
    else:
        print("\n[ERROR] Hubo problemas en la compilación.")
    
    input("\nPresiona Enter para continuar...")
