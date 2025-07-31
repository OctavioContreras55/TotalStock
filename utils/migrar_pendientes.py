# Función utilitaria para migrar pendientes del archivo general a archivos por usuario
# Ejecutar una sola vez si es necesario

import json
from pathlib import Path

def migrar_pendientes_a_usuario(usuario_id, nombre_usuario="Usuario"):
    """
    Migra pendientes del archivo general a un archivo específico de usuario
    """
    archivo_general = Path("data/pendientes.json")
    archivo_usuario = Path(f"data/pendientes_{usuario_id}.json")
    
    if archivo_general.exists() and not archivo_usuario.exists():
        try:
            # Leer pendientes generales
            with open(archivo_general, 'r', encoding='utf-8') as f:
                pendientes = json.load(f)
            
            # Añadir información de usuario a cada pendiente
            for pendiente in pendientes:
                pendiente['usuario_id'] = usuario_id
                pendiente['usuario_nombre'] = nombre_usuario
            
            # Guardar en archivo específico del usuario
            with open(archivo_usuario, 'w', encoding='utf-8') as f:
                json.dump(pendientes, f, ensure_ascii=False, indent=2)
            
            print(f"Pendientes migrados para usuario {nombre_usuario} ({usuario_id})")
            return True
            
        except Exception as e:
            print(f"Error al migrar pendientes: {e}")
            return False
    
    return False

# Ejemplo de uso:
# migrar_pendientes_a_usuario("firebase_user_id_123", "Octavio")
