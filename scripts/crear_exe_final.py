#!/usr/bin/env python3
"""
Script final para crear ejecutable sin errores async
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def crear_ejecutable_final():
    """Crear ejecutable con todas las correcciones aplicadas"""
    
    print("🔧 TotalStock - Ejecutable Final (Sin Errores Async)")
    print("=" * 60)
    print("🐛 Solucionando problema de await...")
    
    # Limpiar build anterior
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"🧹 Limpiando: {carpeta}/")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Verificar correcciones aplicadas
    print("✅ Verificando correcciones aplicadas:")
    
    # Verificar que run.py no tenga await login_view
    with open("run.py", "r", encoding="utf-8") as f:
        contenido_run = f.read()
        if "await login_view" in contenido_run:
            print("❌ Error: run.py aún tiene 'await login_view'")
            print("💡 El archivo run.py debe tener: login_view(page, cargar_pantalla_principal)")
            return False
        else:
            print("   • ✅ run.py: await corregido")
    
    # Verificar que firebase.py tenga la función de rutas
    with open("conexiones/firebase.py", "r", encoding="utf-8") as f:
        contenido_firebase = f.read()
        if "obtener_ruta_recurso" in contenido_firebase:
            print("   • ✅ firebase.py: rutas dinámicas implementadas")
        else:
            print("❌ Error: firebase.py no tiene la función obtener_ruta_recurso")
            return False
    
    # Verificar credenciales
    if os.path.exists("conexiones/credenciales_firebase.json"):
        print("   • ✅ credenciales_firebase.json: encontrado")
    else:
        print("❌ Error: credenciales_firebase.json no encontrado")
        return False
    
    print("\n🚀 Creando ejecutable final...")
    
    # Comando PyInstaller optimizado
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed", 
        "--name=TotalStock",
        "--noconfirm",
        # Agregar datos con rutas específicas
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        "--add-data=data;data",
        # Importaciones críticas
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=flet.security",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        "--hidden-import=google.cloud.firestore",
        "--hidden-import=polars",
        "--hidden-import=openpyxl",
        "--hidden-import=asyncio",
        # Recopilar módulos completos
        "--collect-all=flet",
        "--collect-all=firebase_admin",
        # Excluir módulos innecesarios para reducir tamaño
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib", 
        "--exclude-module=numpy",
    ]
    
    # Agregar icono si existe
    if os.path.exists("assets/logo.ico"):
        comando.extend(["--icon", "assets/logo.ico"])
        print("🎨 Incluyendo icono")
    
    # Archivo principal
    comando.append("run.py")
    
    print("⏳ Construyendo ejecutable (puede tomar varios minutos)...")
    
    try:
        resultado = subprocess.run(comando, check=True)
        
        # Verificar resultado
        exe_path = Path("dist/TotalStock.exe")
        if exe_path.exists():
            tamaño_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ ¡Ejecutable creado exitosamente!")
            print(f"📁 Ubicación: {exe_path.absolute()}")
            print(f"📊 Tamaño: {tamaño_mb:.1f} MB")
            
            print(f"\n🎉 ¡PROCESO COMPLETADO!")
            print("🔧 **TODAS LAS CORRECCIONES APLICADAS:**")
            print("   • ✅ Error 'await login_view' → CORREGIDO")
            print("   • ✅ Error 'credenciales Firebase' → CORREGIDO") 
            print("   • ✅ Rutas dinámicas → IMPLEMENTADAS")
            print("   • ✅ Importaciones async → OPTIMIZADAS")
            
            print(f"\n📋 **LISTO PARA USAR:**")
            print("1. 🧪 Ejecuta: dist/TotalStock.exe")
            print("2. 🔐 Prueba el login")
            print("3. 📊 Verifica todas las funcionalidades")
            print("4. 🚀 ¡Distribuye tu aplicación!")
            
            return True
        else:
            print("❌ No se encontró el ejecutable generado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar PyInstaller: {e}")
        return False

if __name__ == "__main__":
    success = crear_ejecutable_final()
    
    if success:
        print("\n🎯 ¡EJECUTABLE FINAL LISTO! Sin errores async ni Firebase.")
    else:
        print("\n❌ Hubo un problema. Revisa los errores anteriores.")
    
    input("\nPresiona Enter para continuar...")
