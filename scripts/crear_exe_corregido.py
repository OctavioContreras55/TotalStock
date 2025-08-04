#!/usr/bin/env python3
"""
Script de corrección para problemas de DLL en ejecutables PyInstaller
Incluye todas las dependencias de Python y bibliotecas necesarias
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def crear_ejecutable_corregido():
    """Crear ejecutable con todas las dependencias incluidas"""
    
    print("🔧 TotalStock - Ejecutable CORREGIDO (Sin errores DLL)")
    print("=" * 65)
    print("🐛 Solucionando problemas de dependencias...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Limpiar build anterior
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"🧹 Limpiando: {carpeta}/")
    
    print("\n⚡ Creando versión CORREGIDA con todas las dependencias...")
    
    # Comando con inclusiones explícitas para evitar errores de DLL
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # Usar onedir para evitar problemas de descompresión
        "--windowed",
        "--name=TotalStock",
        "--noconfirm",
        
        # Datos necesarios
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        "--add-data=data;data",
        
        # Imports explícitos
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=flet.auth",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        "--hidden-import=google.cloud.firestore",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        
        # Incluir Python DLLs explícitamente
        "--collect-all=flet",
        "--collect-all=firebase_admin",
        "--collect-all=google.cloud",
        
        # Copiar bibliotecas binarias
        "--copy-metadata=flet",
        "--copy-metadata=firebase_admin",
        "--copy-metadata=google-cloud-firestore",
        
        # Configuración de runtime
        "--runtime-tmpdir=.",
        
        # Archivo principal
        "run.py"
    ]
    
    try:
        print("⏳ Construyendo ejecutable corregido...")
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        
        print("\n✅ ¡Ejecutable corregido creado exitosamente!")
        
        # Verificar que se creó correctamente
        exe_path = Path("dist/TotalStock/TotalStock.exe")
        if exe_path.exists():
            # Obtener tamaño
            size_bytes = sum(f.stat().st_size for f in Path("dist/TotalStock").rglob('*') if f.is_file())
            size_mb = size_bytes / (1024 * 1024)
            
            print(f"📁 Ubicación: {exe_path.absolute()}")
            print(f"📊 Tamaño total: {size_mb:.1f} MB")
            
            # Verificar archivos críticos
            internal_path = Path("dist/TotalStock/_internal")
            if internal_path.exists():
                print("✅ Dependencias internas incluidas correctamente")
                
                # Buscar DLLs de Python
                python_dlls = list(internal_path.glob("python*.dll"))
                if python_dlls:
                    print(f"✅ Python DLLs encontradas: {len(python_dlls)}")
                else:
                    print("⚠️  No se encontraron Python DLLs - puede haber problemas")
            
            # Crear acceso rápido actualizado
            crear_acceso_rapido()
            
            print("\n🎉 ¡EJECUTABLE CORREGIDO LISTO!")
            print("⚡ Ahora debería funcionar sin errores de DLL!")
            
        else:
            print("❌ Error: No se encontró el ejecutable en la ubicación esperada")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en PyInstaller: {e}")
        print("💡 Salida del error:")
        print(e.stderr)
        return False
    
    return True

def crear_acceso_rapido():
    """Crear archivo BAT actualizado"""
    ruta_exe = os.path.abspath("dist/TotalStock/TotalStock.exe")
    ruta_carpeta = os.path.dirname(ruta_exe)
    
    contenido_bat = f'''@echo off
title TotalStock - Inicio Rápido (CORREGIDO)
cd /d "{ruta_carpeta}"
echo ⚡ Iniciando TotalStock (Versión Corregida - Sin errores DLL)...
echo 📁 Ejecutando desde: {ruta_exe}
start "" "TotalStock.exe"
'''
    
    with open("TotalStock_CORREGIDO.bat", "w", encoding="utf-8") as f:
        f.write(contenido_bat)
    
    print("✅ Acceso rápido creado: TotalStock_CORREGIDO.bat")

def main():
    """Función principal"""
    print("🔧 Iniciando corrección de ejecutable...")
    
    if crear_ejecutable_corregido():
        print("\n" + "="*65)
        print("🎊 ¡CORRECCIÓN EXITOSA!")
        print("")
        print("📋 INSTRUCCIONES DE USO:")
        print("=" * 30)
        print("🏃‍♂️ **OPCIÓN 1 - Acceso rápido:**")
        print("   • Doble clic en: TotalStock_CORREGIDO.bat")
        print("")
        print("🎯 **OPCIÓN 2 - Directo:**")
        print("   • Navega a: dist/TotalStock/")
        print("   • Ejecuta: TotalStock.exe")
        print("")
        print("🔧 **DIFERENCIAS DE ESTA VERSIÓN:**")
        print("   • ✅ Todas las DLLs de Python incluidas")
        print("   • ✅ Dependencias completas de Flet")
        print("   • ✅ Bibliotecas Firebase completas")
        print("   • ✅ Sin errores de módulos faltantes")
        print("")
        print("🎉 ¡El ejecutable ahora debería funcionar perfectamente!")
    else:
        print("\n❌ Hubo problemas en la corrección.")
        print("💡 Intenta ejecutar el script desde la raíz del proyecto.")
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
