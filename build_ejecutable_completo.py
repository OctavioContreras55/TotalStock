#!/usr/bin/env python3
"""
Script para construir el ejecutable de TotalStock con todas las dependencias
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def limpiar_directorios():
    """Limpiar directorios de construcción anteriores"""
    print("🧹 Limpiando directorios de construcción anteriores...")
    
    directorios_a_limpiar = ['build', 'dist', '__pycache__']
    for directorio in directorios_a_limpiar:
        if os.path.exists(directorio):
            try:
                shutil.rmtree(directorio)
                print(f"   ✅ Eliminado: {directorio}")
            except Exception as e:
                print(f"   ❌ Error eliminando {directorio}: {e}")

def verificar_dependencias():
    """Verificar que todas las dependencias estén instaladas"""
    print("📦 Verificando dependencias...")
    
    dependencias = [
        'flet',
        'firebase_admin',  # Nombre del módulo para import
        'polars',
        'openpyxl',
        'xlsxwriter',
        'reportlab',
        'PyInstaller'  # Nombre del módulo para import
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - INSTALANDO...")
            # Usar nombre del paquete para pip install
            pip_name = dep
            if dep == 'firebase_admin':
                pip_name = 'firebase-admin'
            elif dep == 'PyInstaller':
                pip_name = 'pyinstaller'
            
            subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name], check=True)

def crear_spec_optimizado():
    """Crear archivo .spec optimizado para Windows"""
    print("📄 Creando archivo .spec optimizado...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Datos adicionales que necesita la aplicación
added_files = [
    ('assets', 'assets'),
    ('conexiones/credenciales_firebase.json', 'conexiones'),
    ('data', 'data'),
]

# Imports ocultos críticos para Firebase y Flet
hidden_imports = [
    # Firebase
    'firebase_admin',
    'firebase_admin.credentials',
    'firebase_admin.firestore',
    'google.cloud.firestore',
    'google.cloud.firestore_v1',
    'google.cloud.firestore_v1.services',
    'google.cloud.firestore_v1.types',
    'google.auth',
    'google.auth.transport',
    'google.auth.transport.requests',
    'grpc',
    'grpc._cython',
    
    # Flet y UI
    'flet',
    'flet.core',
    'flet.fastapi',
    
    # Herramientas de datos
    'polars',
    'openpyxl',
    'xlsxwriter', 
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.pdfgen.canvas',
    'reportlab.lib.pagesizes',
    'reportlab.lib.colors',
    'reportlab.platypus',
    
    # Python estándar crítico
    'asyncio',
    'threading',
    'json',
    'datetime',
    'pathlib',
    'tempfile',
    'subprocess',
    'socket',
    'ssl',
    'concurrent.futures',
    'weakref',
]

# Binarios adicionales para incluir (DLLs de Python)
binaries = []

# Análisis del script principal
a = Analysis(
    ['run.py'],
    pathex=[os.path.abspath('.')],
    binaries=binaries,
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',  # Usamos polars en su lugar
        'IPython',
        'jupyter',
        'notebook',
        'qtpy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Compilación
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EJECUTABLE ÚNICO (onefile) - Esto resuelve el problema de DLL
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TotalStock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola para aplicación GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico' if os.path.exists('assets/logo.ico') else None,
    version_file=None,
    uac_admin=False,
)
'''
    
    with open('TotalStock_OPTIMIZADO.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   ✅ Archivo .spec optimizado creado")

def construir_ejecutable():
    """Construir el ejecutable usando PyInstaller"""
    print("🔨 Construyendo ejecutable...")
    
    # Comando PyInstaller optimizado usando python -m
    comando = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'TotalStock_OPTIMIZADO.spec'
    ]
    
    print(f"   Ejecutando: {' '.join(comando)}")
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print("   ✅ Construcción exitosa")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error en construcción:")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def verificar_resultado():
    """Verificar que el ejecutable se creó correctamente"""
    print("🔍 Verificando resultado...")
    
    ejecutable_path = 'dist/TotalStock.exe'
    if os.path.exists(ejecutable_path):
        tamaño = os.path.getsize(ejecutable_path) / (1024 * 1024)  # MB
        print(f"   ✅ Ejecutable creado: {ejecutable_path}")
        print(f"   📊 Tamaño: {tamaño:.1f} MB")
        
        # Verificar estructura
        print("   📁 Estructura del directorio dist:")
        for item in os.listdir('dist'):
            item_path = os.path.join('dist', item)
            if os.path.isfile(item_path):
                size_mb = os.path.getsize(item_path) / (1024 * 1024)
                print(f"      📄 {item} ({size_mb:.1f} MB)")
            else:
                print(f"      📁 {item}/")
        
        return True
    else:
        print(f"   ❌ No se encontró el ejecutable en: {ejecutable_path}")
        return False

def main():
    """Función principal del script de construcción"""
    print("🚀 INICIANDO CONSTRUCCIÓN DE TOTALSTOCK")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('run.py'):
        print("❌ Error: No se encontró run.py. Ejecuta este script desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    try:
        # Paso 1: Limpiar
        limpiar_directorios()
        print()
        
        # Paso 2: Verificar dependencias
        verificar_dependencias()
        print()
        
        # Paso 3: Crear .spec optimizado
        crear_spec_optimizado()
        print()
        
        # Paso 4: Construir
        if construir_ejecutable():
            print()
            
            # Paso 5: Verificar resultado
            if verificar_resultado():
                print()
                print("🎉 ¡CONSTRUCCIÓN COMPLETADA EXITOSAMENTE!")
                print("📦 El ejecutable está en: dist/TotalStock.exe")
                print("💡 Este ejecutable incluye todas las DLLs de Python necesarias")
                print("🚀 Puedes copiarlo a cualquier PC con Windows y debería funcionar")
            else:
                print("❌ Error: El ejecutable no se creó correctamente")
                sys.exit(1)
        else:
            print("❌ Error: Falló la construcción del ejecutable")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
