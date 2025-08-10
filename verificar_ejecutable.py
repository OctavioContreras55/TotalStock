#!/usr/bin/env python3
"""
Script de Verificación del Ejecutable TotalStock
Verifica que el ejecutable funcione correctamente
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import time

def main():
    print("🔍 VERIFICACIÓN DEL EJECUTABLE TOTALSTOCK")
    print("=" * 60)
    
    # Verificar estructura
    verificar_estructura()
    
    # Verificar información de compilación
    verificar_info_compilacion()
    
    # Verificar archivos de acceso
    verificar_archivos_acceso()
    
    # Test básico del ejecutable
    test_ejecutable()
    
    print("\n🎊 ¡VERIFICACIÓN COMPLETADA!")

def verificar_estructura():
    """Verificar que la estructura del ejecutable sea correcta"""
    print("\n📁 Verificando estructura...")
    
    archivos_esperados = [
        "dist/TotalStock/TotalStock.exe",
        "dist/TotalStock/_internal",
        "dist/TotalStock/info_compilacion.json",
        "TotalStock_FUNCIONAL.bat"
    ]
    
    for archivo in archivos_esperados:
        if Path(archivo).exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ FALTA: {archivo}")
    
    # Verificar tamaño del ejecutable
    exe_path = Path("dist/TotalStock/TotalStock.exe")
    if exe_path.exists():
        tamaño_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📏 Tamaño ejecutable: {tamaño_mb:.1f} MB")

def verificar_info_compilacion():
    """Verificar información de compilación"""
    print("\n📊 Verificando información de compilación...")
    
    info_path = Path("dist/TotalStock/info_compilacion.json")
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            print(f"📅 Fecha: {info['fecha_compilacion']}")
            print(f"🐍 Python: {info['version_python']}")
            print(f"📏 Tamaño: {info['tamaño_mb']} MB")
            print(f"⏱️ Tiempo: {info['tiempo_compilacion_segundos']} segundos")
            print("✅ Información de compilación válida")
            
        except Exception as e:
            print(f"❌ Error leyendo info: {e}")
    else:
        print("❌ Archivo de información no encontrado")

def verificar_archivos_acceso():
    """Verificar archivos de acceso directo"""
    print("\n🔗 Verificando archivos de acceso...")
    
    bat_files = [
        "TotalStock_FUNCIONAL.bat",
        "TotalStock_DIRECTO.bat"  # Si existe
    ]
    
    for bat_file in bat_files:
        if Path(bat_file).exists():
            print(f"✅ {bat_file}")
            
            # Verificar contenido
            try:
                with open(bat_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "TotalStock.exe" in content:
                    print(f"   📋 Contenido válido")
                else:
                    print(f"   ⚠️ Contenido incompleto")
            except:
                print(f"   ❌ Error leyendo archivo")

def test_ejecutable():
    """Test básico del ejecutable"""
    print("\n🧪 Test básico del ejecutable...")
    
    exe_path = Path("dist/TotalStock/TotalStock.exe")
    if not exe_path.exists():
        print("❌ Ejecutable no encontrado")
        return
    
    print("⚠️ IMPORTANTE: El test iniciará TotalStock")
    print("   - Se abrirá la aplicación") 
    print("   - Ciérrala manualmente para continuar")
    print("   - Presiona Enter para continuar o Ctrl+C para cancelar")
    
    try:
        input()
        
        print("🚀 Iniciando TotalStock...")
        
        # Ejecutar el ejecutable en background
        process = subprocess.Popen(
            [str(exe_path)],
            cwd=exe_path.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"✅ TotalStock iniciado (PID: {process.pid})")
        print("   👀 Revisa que se haya abierto la ventana")
        print("   🔴 Cierra TotalStock para continuar")
        
        # Esperar un poco
        time.sleep(3)
        
        # Verificar si sigue ejecutándose
        if process.poll() is None:
            print("✅ Proceso ejecutándose correctamente")
        else:
            print("⚠️ Proceso terminó rápidamente")
            print(f"   Código de salida: {process.returncode}")
        
    except KeyboardInterrupt:
        print("\n❌ Test cancelado por usuario")
    except Exception as e:
        print(f"❌ Error en test: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Verificación cancelada")
    
    print("\n" + "="*60)
    print("🏁 Verificación terminada")
    input("Presiona Enter para salir...")
