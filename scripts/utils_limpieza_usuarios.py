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
        print(f"📊 Usuarios encontrados en Firebase: {len(ids_existentes)}")
        return ids_existentes
    except Exception as e:
        print(f"❌ Error al obtener usuarios de Firebase: {e}")
        return []

def encontrar_archivos_usuario():
    """Encuentra todos los archivos de usuario en el directorio data/"""
    patron_config = "data/config_usuario_*.json"
    patron_pendientes = "data/pendientes_*.json"
    
    archivos_config = glob.glob(patron_config)
    archivos_pendientes = glob.glob(patron_pendientes)
    
    todos_archivos = archivos_config + archivos_pendientes
    
    print(f"📁 Archivos de usuario encontrados: {len(todos_archivos)}")
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
    print("🧹 Iniciando limpieza de archivos huérfanos...")
    print(f"📋 Modo: {'PRUEBA' if modo_prueba else 'EJECUCIÓN'}")
    print("=" * 50)
    
    # Obtener usuarios existentes
    usuarios_existentes = obtener_usuarios_firebase()
    if not usuarios_existentes:
        print("❌ No se pudieron obtener los usuarios de Firebase. Abortando limpieza.")
        return
    
    # Encontrar archivos de usuario
    archivos_usuario = encontrar_archivos_usuario()
    if not archivos_usuario:
        print("✅ No se encontraron archivos de usuario para revisar.")
        return
    
    archivos_huerfanos = []
    archivos_validos = []
    
    # Analizar cada archivo
    for archivo in archivos_usuario:
        id_usuario = extraer_id_usuario_de_archivo(archivo)
        
        if not id_usuario:
            print(f"⚠️  No se pudo extraer ID de: {archivo}")
            continue
        
        if id_usuario in usuarios_existentes:
            archivos_validos.append(archivo)
            print(f"✅ Válido: {archivo} (Usuario: {id_usuario})")
        else:
            archivos_huerfanos.append(archivo)
            print(f"🗑️  Huérfano: {archivo} (Usuario inexistente: {id_usuario})")
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN:")
    print(f"   - Archivos válidos: {len(archivos_validos)}")
    print(f"   - Archivos huérfanos: {len(archivos_huerfanos)}")
    
    if archivos_huerfanos:
        if modo_prueba:
            print(f"\n🔍 MODO PRUEBA - Archivos que se eliminarían:")
            for archivo in archivos_huerfanos:
                print(f"   - {archivo}")
            print(f"\n💡 Para ejecutar la limpieza real, ejecute:")
            print(f"   python {__file__} --ejecutar")
        else:
            print(f"\n🗑️  ELIMINANDO archivos huérfanos...")
            eliminados = 0
            errores = 0
            
            for archivo in archivos_huerfanos:
                try:
                    os.remove(archivo)
                    print(f"✅ Eliminado: {archivo}")
                    eliminados += 1
                except Exception as e:
                    print(f"❌ Error al eliminar {archivo}: {e}")
                    errores += 1
            
            print(f"\n📊 RESULTADO FINAL:")
            print(f"   - Archivos eliminados: {eliminados}")
            print(f"   - Errores: {errores}")
            
            if eliminados > 0:
                print("✅ Limpieza completada exitosamente")
            else:
                print("⚠️  No se eliminaron archivos")
    else:
        print("✅ No se encontraron archivos huérfanos. El sistema está limpio.")

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    modo_prueba = "--ejecutar" not in sys.argv
    
    if modo_prueba:
        print("🔍 Ejecutando en MODO PRUEBA")
        print("💡 Usa --ejecutar para eliminar archivos realmente")
    else:
        print("⚠️  MODO EJECUCIÓN: Se eliminarán archivos permanentemente")
        respuesta = input("¿Continuar? (s/N): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada")
            sys.exit(0)
    
    limpiar_archivos_huerfanos(modo_prueba)
