import os
import subprocess
import sys

def menu_principal():
    """Menú principal para seleccionar el tipo de compilación"""
    print("=" * 50)
    print("[INICIO] SISTEMA DE COMPILACIÓN TOTALSTOCK")
    print("=" * 50)
    print("1. [CONFIG] Compilación Básica (rápida)")
    print("2. [RAPIDO] Compilación Optimizada (recomendada)")
    print("3. [DART] Compilación Debug (para desarrollo)")
    print("4. [PACKAGE] Compilación Completa (producción)")
    print("5. [LIMPIEZA] Limpiar archivos temporales")
    print("6. [ERROR] Salir")
    print("=" * 50)
    
    while True:
        try:
            opcion = input("Selecciona una opción (1-6): ")
            
            if opcion == "1":
                ejecutar_script("scripts/build_basico.py")
                break
            elif opcion == "2":
                ejecutar_script("scripts/build_optimizado.py")
                break
            elif opcion == "3":
                ejecutar_script("scripts/build_debug.py")
                break
            elif opcion == "4":
                ejecutar_script("scripts/build_completo.py")
                break
            elif opcion == "5":
                limpiar_archivos()
                break
            elif opcion == "6":
                print("👋 Saliendo...")
                sys.exit(0)
            else:
                print("[ERROR] Opción no válida. Por favor selecciona 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            sys.exit(0)

def ejecutar_script(script_path):
    """Ejecutar script de compilación específico"""
    if not os.path.exists(script_path):
        print(f"[ERROR] Error: No se encontró el script {script_path}")
        return
    
    try:
        print(f"[PROCESO] Ejecutando {script_path}...")
        subprocess.run([sys.executable, script_path], check=True)
        print("[OK] Compilación completada exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error durante la compilación: {e}")
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")

def limpiar_archivos():
    """Limpiar archivos temporales y de compilación"""
    print("[LIMPIEZA] Limpiando archivos temporales...")
    
    directorios_limpiar = ["build", "dist", "__pycache__"]
    archivos_limpiar = ["*.pyc", "*.pyo"]
    
    for directorio in directorios_limpiar:
        if os.path.exists(directorio):
            try:
                import shutil
                shutil.rmtree(directorio)
                print(f"[OK] Eliminado: {directorio}/")
            except Exception as e:
                print(f"[ERROR] Error al eliminar {directorio}: {e}")
    
    print("[OK] Limpieza completada")

if __name__ == "__main__":
    menu_principal()
