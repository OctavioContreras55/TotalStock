#!/usr/bin/env python3
"""
Script de utilidad para limpiar sesiones colgadas de TotalStock
Úsalo si tienes problemas para iniciar sesión por sesiones no cerradas correctamente.
"""

import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def limpiar_sesiones():
    """Limpiar todas las sesiones activas"""
    try:
        from app.utils.sesiones_unicas import gestor_sesiones
        
        print("Limpiando sesiones de TotalStock...")
        
        # Mostrar sesiones actuales
        sesiones_activas = gestor_sesiones.obtener_sesiones_activas()
        if sesiones_activas:
            print(f"Sesiones activas encontradas: {len(sesiones_activas)}")
            for usuario, info in sesiones_activas.items():
                print(f"  - {usuario}: {info.get('fecha_inicio', 'N/A')}")
        else:
            print("No hay sesiones activas")
            return
        
        # Limpiar todas las sesiones
        if gestor_sesiones.limpiar_todas_las_sesiones():
            print("Todas las sesiones han sido limpiadas exitosamente")
            print("Ahora puedes iniciar TotalStock normalmente")
        else:
            print("Error al limpiar sesiones")
            
    except Exception as e:
        print(f"Error durante la limpieza: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("LIMPIADOR DE SESIONES - TotalStock")
    print("=" * 50)
    
    respuesta = input("Estas seguro de que quieres limpiar todas las sesiones? (s/N): ")
    
    if respuesta.lower() in ['s', 'si', 'y', 'yes']:
        limpiar_sesiones()
    else:
        print("Operacion cancelada")
    
    input("\nPresiona Enter para salir...")
