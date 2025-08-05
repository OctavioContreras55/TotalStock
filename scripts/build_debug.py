#!/usr/bin/env python3
"""
Script de compilación debug - Con información de depuración
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_debug():
    """Crear ejecutable con información de debug para desarrollo"""
    
    print("🎯 TotalStock - Compilación Debug")
    print("=" * 50)
    print("🐛 Optimizado para desarrollo y depuración...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Limpiar build anterior
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"🧹 Limpiando: {carpeta}/")
    
    print("\n🔍 Creando versión debug...")
    
    # Comando PyInstaller con información de debug
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--console",  # Mostrar consola para debug
        "--name=TotalStock_Debug",
        "--noconfirm",
        "--debug=all",  # Información de debug completa
        
        # Datos necesarios
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        "--add-data=data;data",
        
        # Importaciones detalladas
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        "--hidden-import=polars",
        "--hidden-import=polars",
        "--hidden-import=openpyxl",
        
        # Conservar archivos temporales para debug
        "--log-level=DEBUG",
        
        "run.py"
    ]
    
    # Agregar icono si existe
    if os.path.exists("assets/logo.ico"):
        comando.extend(["--icon", "assets/logo.ico"])
    
    try:
        print("⏳ Construyendo ejecutable debug (puede tomar más tiempo)...")
        resultado = subprocess.run(comando, check=True)
        
        exe_path = Path("dist/TotalStock_Debug/TotalStock_Debug.exe")
        
        if exe_path.exists():
            # Calcular tamaño
            carpeta_dist = Path("dist/TotalStock_Debug")
            tamaño_total = sum(f.stat().st_size for f in carpeta_dist.rglob('*') if f.is_file())
            tamaño_mb = tamaño_total / (1024 * 1024)
            
            print(f"\n✅ ¡Compilación debug completada!")
            print(f"📁 Ubicación: {exe_path.absolute()}")
            print(f"📊 Tamaño: {tamaño_mb:.1f} MB")
            
            print(f"\n🐛 CARACTERÍSTICAS DEBUG:")
            print("   • ✅ Consola visible para logs")
            print("   • ✅ Información de debug completa")
            print("   • ✅ Archivos temporales conservados")
            print("   • ✅ Log level: DEBUG")
            
            print(f"\n📋 INSTRUCCIONES DE USO:")
            print("🏃‍♂️ Para ejecutar:")
            print(f"   cd {carpeta_dist}")
            print("   ./TotalStock_Debug.exe")
            print("\n💡 La consola mostrará información detallada de depuración")
            
            return True
        else:
            print("❌ Ejecutable no encontrado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en PyInstaller: {e}")
        return False

if __name__ == "__main__":
    success = build_debug()
    
    if success:
        print("\n🎉 ¡Compilación debug lista!")
        print("🐛 Perfecta para desarrollo y solución de problemas")
    else:
        print("\n❌ Hubo problemas en la compilación.")
    
    input("\nPresiona Enter para continuar...")
