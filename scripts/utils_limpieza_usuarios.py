#!/usr/bin/env python3
"""
Utilidad para limpiar archivos huérfanos de usuarios que ya no existen en Firebase.
Esta utilidad puede ejecutarse periódicamente para mantener limpio el directorio data/
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conexiones.firebase import db
import json
import glob

def obtener_usuarios_firebase():
    """Obtiene la lista de IDs de usuarios existentes en Firebase"""
    try:
        usuarios_ref = db.collection('usuarios')
        usuarios = usuarios_ref.get()
        ids_existentes = [usuario.id for usuario in usuarios]
        print(f"[CHART] Usuarios encontrados en Firebase: {len(ids_existentes)}")
        return ids_existentes
    except Exception as e:
        print(f"[ERROR] Error al obtener usuarios de Firebase: {e}")
        return []

def encontrar_archivos_usuario():
    """Encuentra todos los archivos de usuario en el directorio data/"""
    patron_config = "data/config_usuario_*.json"
    patron_pendientes = "data/pendientes_*.json"
    
    archivos_config = glob.glob(patron_config)
    archivos_pendientes = glob.glob(patron_pendientes)
    
    todos_archivos = archivos_config + archivos_pendientes
    
    print(f"[FOLDER] Archivos de usuario encontrados: {len(todos_archivos)}")
    return todos_archivos

def extraer_id_usuario_de_archivo(ruta_archivo):
    """Extrae el ID del usuario del nombre del archivo"""
    nombre_archivo = os.path.basename(ruta_archivo)
    
    if nombre_archivo.startswith("config_usuario_"):
        # config_usuario_ID.json
        return nombre_archivo[15:-5]  # Remover "config_usuario_" y ".json"
    elif nombre_archivo.startswith("pendientes_"):
        # pendientes_ID.json
        return nombre_archivo[11:-5]  # Remover "pendientes_" y ".json"
    
    return None

def limpiar_archivos_huerfanos(modo_prueba=True):
    """
    Limpia archivos de usuarios que ya no existen en Firebase
    
    Args:
        modo_prueba (bool): Si es True, solo muestra qué se eliminaría sin hacerlo
    """
    print("[LIMPIEZA] Iniciando limpieza de archivos huérfanos...")
    print(f"[LISTA] Modo: {'PRUEBA' if modo_prueba else 'EJECUCIÓN'}")
    print("=" * 50)
    
    # Obtener usuarios existentes
    usuarios_existentes = obtener_usuarios_firebase()
    if not usuarios_existentes:
        print("[ERROR] No se pudieron obtener los usuarios de Firebase. Abortando limpieza.")
        return
    
    # Encontrar archivos de usuario
    archivos_usuario = encontrar_archivos_usuario()
    if not archivos_usuario:
        print("[OK] No se encontraron archivos de usuario para revisar.")
        return
    
    archivos_huerfanos = []
    archivos_validos = []
    
    # Analizar cada archivo
    for archivo in archivos_usuario:
        id_usuario = extraer_id_usuario_de_archivo(archivo)
        
        if not id_usuario:
            print(f"[WARN]  No se pudo extraer ID de: {archivo}")
            continue
        
        if id_usuario in usuarios_existentes:
            archivos_validos.append(archivo)
            print(f"[OK] Válido: {archivo} (Usuario: {id_usuario})")
        else:
            archivos_huerfanos.append(archivo)
            print(f"[ELIMINAR]  Huérfano: {archivo} (Usuario inexistente: {id_usuario})")
    
    print("\n" + "=" * 50)
    print(f"[CHART] RESUMEN:")
    print(f"   - Archivos válidos: {len(archivos_validos)}")
    print(f"   - Archivos huérfanos: {len(archivos_huerfanos)}")
    
    if archivos_huerfanos:
        if modo_prueba:
            print(f"\n[BUSCAR] MODO PRUEBA - Archivos que se eliminarían:")
            for archivo in archivos_huerfanos:
                print(f"   - {archivo}")
            print(f"\n[IDEA] Para ejecutar la limpieza real, ejecute:")
            print(f"   python {__file__} --ejecutar")
        else:
            print(f"\n[ELIMINAR]  ELIMINANDO archivos huérfanos...")
            eliminados = 0
            errores = 0
            
            for archivo in archivos_huerfanos:
                try:
                    os.remove(archivo)
                    print(f"[OK] Eliminado: {archivo}")
                    eliminados += 1
                except Exception as e:
                    print(f"[ERROR] Error al eliminar {archivo}: {e}")
                    errores += 1
            
            print(f"\n[CHART] RESULTADO FINAL:")
            print(f"   - Archivos eliminados: {eliminados}")
            print(f"   - Errores: {errores}")
            
            if eliminados > 0:
                print("[OK] Limpieza completada exitosamente")
            else:
                print("[WARN]  No se eliminaron archivos")
    else:
        print("[OK] No se encontraron archivos huérfanos. El sistema está limpio.")

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    modo_prueba = "--ejecutar" not in sys.argv
    
    if modo_prueba:
        print("[BUSCAR] Ejecutando en MODO PRUEBA")
        print("[IDEA] Usa --ejecutar para eliminar archivos realmente")
    else:
        print("[WARN]  MODO EJECUCIÓN: Se eliminarán archivos permanentemente")
        respuesta = input("¿Continuar? (s/N): ")
        if respuesta.lower() != 's':
            print("[ERROR] Operación cancelada")
            sys.exit(0)
    
    limpiar_archivos_huerfanos(modo_prueba)
