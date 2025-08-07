#!/usr/bin/env python3
"""
Script de limpieza automática para TotalStock
Elimina archivos temporales, cache y directorios de compilación
"""

import os
import shutil
import sys
from pathlib import Path

def limpiar_proyecto():
    """Ejecutar limpieza completa del proyecto"""
    
    print("🧹 TotalStock - Limpieza Automática del Proyecto")
    print("=" * 50)
    
    # Obtener directorio raíz del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Elementos a limpiar
    elementos_limpieza = {
        "directorios": [
            "build",
            "dist", 
            "__pycache__"
        ],
        "archivos": [
            "*.pyc",
            "*.pyo", 
            "*.pyd",
            ".DS_Store",
            "Thumbs.db"
        ],
        "cache_recursivo": [
            "__pycache__",
            ".pytest_cache",
            ".coverage"
        ]
    }
    
    # 1. Limpiar directorios principales
    print("\n🗂️ Limpiando directorios principales...")
    for directorio in elementos_limpieza["directorios"]:
        if os.path.exists(directorio):
            try:
                shutil.rmtree(directorio)
                print(f"   ✅ Eliminado: {directorio}/")
            except Exception as e:
                print(f"   ❌ Error eliminando {directorio}: {e}")
        else:
            print(f"   ⚪ No existe: {directorio}/")
    
    # 2. Limpiar cache recursivamente
    print("\n📁 Limpiando cache recursivo...")
    for cache_dir in elementos_limpieza["cache_recursivo"]:
        for root, dirs, files in os.walk("."):
            if cache_dir in dirs:
                cache_path = os.path.join(root, cache_dir)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   ✅ Eliminado: {cache_path}")
                except Exception as e:
                    print(f"   ❌ Error eliminando {cache_path}: {e}")
    
    # 3. Limpiar archivos por patrón
    print("\n📄 Limpiando archivos temporales...")
    import glob
    for patron in elementos_limpieza["archivos"]:
        archivos_encontrados = glob.glob(f"**/{patron}", recursive=True)
        for archivo in archivos_encontrados:
            try:
                os.remove(archivo)
                print(f"   ✅ Eliminado: {archivo}")
            except Exception as e:
                print(f"   ❌ Error eliminando {archivo}: {e}")
    
    # 4. Estadísticas finales
    print("\n📊 Estadísticas de limpieza:")
    tamano_actual = calcular_tamano_proyecto()
    print(f"   📁 Tamaño actual del proyecto: {tamano_actual:.2f} MB")
    
    print("\n✅ ¡Limpieza completada!")
    print("🎯 El proyecto está listo para:")
    print("   • 🚀 Nueva compilación")
    print("   • 📤 Distribución") 
    print("   • 🔄 Control de versiones")

def calcular_tamano_proyecto():
    """Calcular tamaño total del proyecto en MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk("."):
        # Excluir directorios que no necesitamos contar
        dirnames[:] = [d for d in dirnames if d not in ['.git', 'node_modules', 'venv', '.venv']]
        
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    
    return total_size / (1024 * 1024)  # Convertir a MB

if __name__ == "__main__":
    try:
        limpiar_proyecto()
        input("\n⏸️ Presiona Enter para continuar...")
    except KeyboardInterrupt:
        print("\n\n👋 Limpieza cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        input("\n⏸️ Presiona Enter para continuar...")
        sys.exit(1)
