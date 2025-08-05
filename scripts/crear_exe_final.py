#!/usr/bin/env python3
"""
TotalStock - Script de compilación FINAL
Crea ejecutable en archivo único para distribución fácil
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def main():
    print("📦 TotalStock - Ejecutable FINAL (Archivo Único)")
    print("=" * 60)
    print("🚀 Creando versión portátil para distribución...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Limpiar compilaciones anteriores
    print("\n🧹 Limpiando compilaciones anteriores...")
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"✅ Limpiado: {carpeta}/")
    
    print("\n📦 Creando versión ONEFILE (archivo único)...")
    print("⏳ Construyendo ejecutable final...")
    
    # Comando PyInstaller para archivo único
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Archivo único
        "--windowed",  # Sin consola
        "--name=TotalStock",
        "--noconfirm",  # No preguntar sobre sobrescribir
        
        # Datos necesarios
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        "--add-data=data;data",
        
        # Importaciones específicas
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        "--hidden-import=polars",
        "--hidden-import=polars",
        "--hidden-import=openpyxl",
        
        # Optimizaciones para archivo único
        "--optimize=2",  # Optimización máxima
        
        # Archivo principal
        "run.py"
    ]
    
    # Agregar icono si existe
    if os.path.exists("assets/logo.ico"):
        comando.extend(["--icon", "assets/logo.ico"])
    
    try:
        # Ejecutar PyInstaller
        start_time = time.time()
        resultado = subprocess.run(comando, check=True)
        end_time = time.time()
        
        # Verificar resultado
        exe_path = Path("dist/TotalStock.exe")
        
        if exe_path.exists():
            # Calcular estadísticas
            tamaño_mb = exe_path.stat().st_size / (1024 * 1024)
            tiempo_compilacion = end_time - start_time
            
            # Crear acceso directo
            crear_acceso_directo()
            
            print(f"\n✅ ¡Ejecutable FINAL creado!")
            print(f"📁 Ubicación: {exe_path.absolute()}")
            print(f"📊 Tamaño: {tamaño_mb:.1f} MB")
            print(f"⏱️  Tiempo de compilación: {tiempo_compilacion:.1f} segundos")
            print("✅ Acceso rápido creado: TotalStock_FINAL.bat")
            
            print(f"\n🎉 ¡COMPILACIÓN FINAL EXITOSA!")
            print("📦 **VENTAJAS de esta versión:**")
            print("   • 📁 Un solo archivo ejecutable")
            print("   • 📤 Súper fácil de distribuir")
            print("   • 💾 No necesita instalación")
            print("   • 🔧 Funciona en cualquier Windows")
            
            mostrar_instrucciones(exe_path)
            
            return True
        else:
            print("❌ Error: No se pudo crear el ejecutable")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en PyInstaller: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def crear_acceso_directo():
    """Crear archivo BAT para acceso directo"""
    contenido_bat = f'''@echo off
cd /d "{os.getcwd()}"
start "" "dist\\TotalStock.exe"
'''
    
    with open("TotalStock_FINAL.bat", "w", encoding="utf-8") as f:
        f.write(contenido_bat)

def mostrar_instrucciones(exe_path):
    """Mostrar instrucciones de uso"""
    print(f"\n📋 INSTRUCCIONES DE USO:")
    print("=" * 30)
    print("🏃‍♂️ **PARA EJECUTAR:**")
    print(f"   • Doble clic en: {exe_path}")
    print("   • O usar: TotalStock_FINAL.bat")
    print()
    print("📤 **PARA DISTRIBUIR:**")
    print(f"   • Enviar archivo: {exe_path}")
    print("   • Solo 1 archivo, súper fácil")
    print("   • No necesita instalación")
    print()
    print("⚠️  **NOTA IMPORTANTE:**")
    print("   • Primera ejecución: 8-15 segundos")
    print("   • Siguientes ejecuciones: más rápido")
    print("   • Windows puede mostrar advertencia de seguridad")
    print()
    print("🎊 ¡EJECUTABLE FINAL LISTO!")
    print("📦 Perfecto para distribución!")

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Compilación completada exitosamente")
    else:
        print("\n❌ Hubo problemas en la compilación.")
    
    input("\nPresiona Enter para continuar...")
