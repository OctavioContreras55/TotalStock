#!/usr/bin/env python3
"""
Script para crear icono (.ico) desde el logo existente
"""

import os
from pathlib import Path

def crear_icono():
    """Crear archivo .ico desde logo.png"""
    logo_path = Path("assets/logo.png")
    ico_path = Path("assets/logo.ico")
    
    if not logo_path.exists():
        print("❌ No se encontró assets/logo.png")
        return False
    
    try:
        # Intentar con Pillow
        from PIL import Image
        
        print("🎨 Convirtiendo logo.png a logo.ico...")
        
        # Abrir imagen
        img = Image.open(logo_path)
        
        # Crear diferentes tamaños para el icono
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Guardar como ICO
        img.save(ico_path, format='ICO', sizes=sizes)
        
        print(f"✅ Icono creado: {ico_path}")
        return True
        
    except ImportError:
        print("📦 Pillow no está instalado. Instalando...")
        try:
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
            
            # Intentar de nuevo
            from PIL import Image
            img = Image.open(logo_path)
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save(ico_path, format='ICO', sizes=sizes)
            
            print(f"✅ Icono creado: {ico_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al instalar Pillow: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear icono: {e}")
        return False

if __name__ == "__main__":
    print("🎨 TotalStock - Generador de Icono")
    print("=" * 40)
    crear_icono()
