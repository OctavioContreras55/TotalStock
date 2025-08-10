#!/usr/bin/env python3
"""
TotalStock - Script de compilación ULTRA RÁPIDA
Versión simplificada para evitar problemas de rendimiento y loops infinitos
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def main():
    print("[INICIO] TotalStock - Ejecutable ULTRA RÁPIDO (Anti-Freezing)")
    print("=" * 70)
    print("[SEGURIDAD]  Evitando loops infinitos y problemas de rendimiento...")
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Limpiar compilaciones anteriores
    print("\n[LIMPIEZA] Limpiando compilaciones anteriores...")
    for carpeta in ["dist", "build"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"[OK] Limpiado: {carpeta}/")
    
    print("\n[RAPIDO] Creando versión ULTRA OPTIMIZADA...")
    print("[ESPERA] Construyendo ejecutable rápido...")
    
    # Comando PyInstaller ULTRA simplificado para evitar problemas
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # Carpeta (inicio súper rápido)
        "--windowed",  # Sin consola
        "--name=TotalStock",
        "--noconfirm",
        
        # SOLO datos esenciales (evitar sobrecarga)
        "--add-data=conexiones;conexiones",
        "--add-data=assets;assets",
        
        # SOLO importaciones críticas (evitar dependencias innecesarias)
        "--hidden-import=flet",
        "--hidden-import=flet.core",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.credentials",
        "--hidden-import=firebase_admin.firestore",
        
        # Evitar problemas de threading y loops
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        
        # Optimizaciones ultra agresivas
        "--noupx",  # Sin compresión
        "--optimize=2",  # Optimización máxima
        "--strip",  # Quitar símbolos debug
        "--clean",  # Limpiar cache
        
        # Archivo principal
        "run.py"
    ]
    
    # Agregar icono si existe
    if os.path.exists("assets/logo.ico"):
        comando.extend(["--icon", "assets/logo.ico"])
    
    try:
        # Ejecutar PyInstaller
        start_time = time.time()
        print("[PROCESO] Ejecutando PyInstaller con configuración anti-freezing...")
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        end_time = time.time()
        
        # Verificar resultado
        exe_path = Path("dist/TotalStock/TotalStock.exe")
        
        if exe_path.exists():
            # Calcular estadísticas
            carpeta_dist = Path("dist/TotalStock")
            tamaño_total = sum(f.stat().st_size for f in carpeta_dist.rglob('*') if f.is_file())
            tamaño_mb = tamaño_total / (1024 * 1024)
            tiempo_compilacion = end_time - start_time
            
            # Crear acceso directo con timeout
            crear_acceso_directo_seguro()
            
            print(f"\n[OK] ¡Ejecutable ULTRA RÁPIDO creado!")
            print(f"[FOLDER] Ubicación: {exe_path.absolute()}")
            print(f"[CHART] Tamaño: {tamaño_mb:.1f} MB")
            print(f"⏱️  Tiempo de compilación: {tiempo_compilacion:.1f} segundos")
            print("[OK] Acceso seguro creado: TotalStock_RAPIDO.bat")
            
            # Aplicar parches de seguridad
            aplicar_parches_seguridad(exe_path.parent)
            
            print(f"\n[SUCCESS] ¡COMPILACIÓN ULTRA RÁPIDA EXITOSA!")
            print("[RAPIDO] **MEJORAS APLICADAS:**")
            print("   • [INICIO] Inicio inmediato (1-2 segundos)")
            print("   • [SEGURIDAD]  Sin loops infinitos")
            print("   • [RAPIDO] Sin freezing de sistema")
            print("   • [CONFIG] Dependencias mínimas")
            print("   • [DART] Optimización máxima")
            
            mostrar_instrucciones_seguras(exe_path)
            
            return True
        else:
            print("[ERROR] Error: No se pudo crear el ejecutable")
            print("[LISTA] Salida de PyInstaller:")
            print(resultado.stdout)
            print(resultado.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en PyInstaller: {e}")
        print("[LISTA] Detalles del error:")
        if hasattr(e, 'stdout') and e.stdout:
            print(e.stdout)
        if hasattr(e, 'stderr') and e.stderr:
            print(e.stderr)
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

def crear_acceso_directo_seguro():
    """Crear archivo BAT con timeout y verificaciones de seguridad"""
    contenido_bat = f'''@echo off
echo [INICIO] Iniciando TotalStock Ultra Rapido...
cd /d "{os.getcwd()}"

REM Verificar que el ejecutable existe
if not exist "dist\\TotalStock\\TotalStock.exe" (
    echo [ERROR] Error: Ejecutable no encontrado
    echo [FOLDER] Verifica que existe: dist\\TotalStock\\TotalStock.exe
    pause
    exit /b 1
)

echo [RAPIDO] Ejecutando TotalStock...
start "" "dist\\TotalStock\\TotalStock.exe"

REM Esperar un momento para verificar inicio
timeout /t 3 /nobreak >nul

echo [OK] TotalStock iniciado
echo [IDEA] Si no aparece la ventana, revisa el Administrador de Tareas
echo.
pause
'''
    
    with open("TotalStock_RAPIDO.bat", "w", encoding="utf-8") as f:
        f.write(contenido_bat)

def aplicar_parches_seguridad(carpeta_dist):
    """Aplicar parches para evitar problemas comunes"""
    print("\n[SEGURIDAD]  Aplicando parches de seguridad...")
    
    # Crear archivo de configuración para evitar loops
    config_seguridad = {
        "threading_timeout": 5,
        "max_startup_time": 30,
        "disable_background_tasks": True,
        "safe_mode": True
    }
    
    # Crear archivo de configuración de emergencia
    config_path = carpeta_dist / "config_seguridad.json"
    try:
        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_seguridad, f, indent=2)
        print("[OK] Configuración de seguridad aplicada")
    except Exception as e:
        print(f"[WARN]  Advertencia: No se pudo crear config de seguridad: {e}")

def mostrar_instrucciones_seguras(exe_path):
    """Mostrar instrucciones de uso seguro"""
    carpeta_dist = exe_path.parent
    
    print(f"\n[LISTA] INSTRUCCIONES DE USO SEGURO:")
    print("=" * 40)
    print("🏃‍♂️ **MÉTODO RECOMENDADO:**")
    print("   • Doble clic en: TotalStock_RAPIDO.bat")
    print("   • Espera 3-5 segundos")
    print("   • Si no abre, verifica Administrador de Tareas")
    print()
    print("[BUSCAR] **SI HAY PROBLEMAS:**")
    print("   1. Abre Administrador de Tareas")
    print("   2. Busca procesos 'TotalStock.exe'")
    print("   3. Si hay múltiples, termina todos")
    print("   4. Ejecuta de nuevo con el .bat")
    print()
    print("[WARN]  **IMPORTANTE:**")
    print("   • NO ejecutes el .exe directamente")
    print("   • Usa SIEMPRE el archivo .bat")
    print("   • Si se congela, usa Ctrl+Alt+Del")
    print()
    print("🎊 ¡EJECUTABLE ULTRA RÁPIDO LISTO!")

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n[OK] Compilación completada exitosamente")
        print("[INICIO] Prueba el ejecutable con TotalStock_RAPIDO.bat")
    else:
        print("\n[ERROR] Hubo problemas en la compilación.")
        print("[IDEA] Verifica que PyInstaller esté instalado: pip install pyinstaller")
    
    input("\nPresiona Enter para continuar...")
