#!/usr/bin/env python3
"""
Script automático para limpiar sesiones zombie de TotalStock
Se ejecuta automáticamente para limpiar sesiones de procesos que ya no existen.
"""

import sys
import os
import subprocess
import json
import tempfile

def limpiar_sesiones_zombie():
    """Limpiar sesiones de procesos que ya no existen"""
    try:
        sesiones_file = os.path.join(tempfile.gettempdir(), "totalstock_sesiones.json")
        
        if not os.path.exists(sesiones_file):
            print("No hay archivo de sesiones")
            return True
            
        # Cargar sesiones
        with open(sesiones_file, 'r', encoding='utf-8') as f:
            sesiones = json.load(f)
        
        if not sesiones:
            print("No hay sesiones activas")
            return True
        
        print(f"Verificando {len(sesiones)} sesiones...")
        sesiones_limpias = {}
        sesiones_eliminadas = 0
        
        for usuario, info_sesion in sesiones.items():
            proceso_id = info_sesion.get('proceso_id')
            if proceso_id:
                try:
                    # Verificar si el proceso existe
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {proceso_id}'], 
                                          capture_output=True, text=True, timeout=5)
                    
                    if f'{proceso_id}' in result.stdout:
                        # Proceso existe, mantener sesión
                        sesiones_limpias[usuario] = info_sesion
                        print(f"Sesion activa: {usuario} (PID: {proceso_id})")
                    else:
                        # Proceso no existe, eliminar sesión
                        print(f"Sesion zombie eliminada: {usuario} (PID: {proceso_id})")
                        sesiones_eliminadas += 1
                        
                except Exception as e:
                    print(f"Error verificando proceso {proceso_id}: {e}")
                    # En caso de error, mantener la sesión por seguridad
                    sesiones_limpias[usuario] = info_sesion
            else:
                # Sin proceso ID, mantener por seguridad
                sesiones_limpias[usuario] = info_sesion
                print(f"Sesion sin PID: {usuario}")
        
        # Guardar sesiones limpias
        with open(sesiones_file, 'w', encoding='utf-8') as f:
            json.dump(sesiones_limpias, f, indent=2, ensure_ascii=False)
        
        if sesiones_eliminadas > 0:
            print(f"Eliminadas {sesiones_eliminadas} sesiones zombie")
        else:
            print("No se encontraron sesiones zombie")
            
        return True
        
    except Exception as e:
        print(f"Error limpiando sesiones zombie: {e}")
        return False

if __name__ == "__main__":
    print("LIMPIADOR AUTOMATICO DE SESIONES ZOMBIE")
    print("=" * 50)
    
    if limpiar_sesiones_zombie():
        print("Limpieza completada exitosamente")
    else:
        print("Error durante la limpieza")
