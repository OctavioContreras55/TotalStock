#!/usr/bin/env python3
"""
Script de compilación optimizada - Alias para crear_exe_optimizado.py
"""

import os
import sys
import subprocess

def build_optimizado():
    """Ejecutar el script de compilación optimizada existente"""
    
    print("⚡ TotalStock - Compilación Optimizada")
    print("=" * 50)
    print("🔄 Redirigiendo al script optimizado existente...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    
    # Script optimizado existente
    script_optimizado = os.path.join(script_dir, "crear_exe_optimizado.py")
    
    if os.path.exists(script_optimizado):
        try:
            print(f"🚀 Ejecutando: {script_optimizado}")
            resultado = subprocess.run([sys.executable, script_optimizado], 
                                     cwd=root_dir, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando script optimizado: {e}")
            return False
    else:
        print(f"❌ No se encontró el script: {script_optimizado}")
        return False

if __name__ == "__main__":
    success = build_optimizado()
    
    if not success:
        print("\n❌ Error en la compilación optimizada.")
        input("\nPresiona Enter para continuar...")
