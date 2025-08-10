"""
Módulo para actualizar el dashboard dinámicamente desde cualquier parte de la aplicación
"""
import asyncio

# Variable global para almacenar la función de actualización
_funcion_actualizacion = None
_page_ref = None

def registrar_actualizador(funcion_actualizacion, page):
    """Registra la función de actualización del dashboard"""
    global _funcion_actualizacion, _page_ref
    _funcion_actualizacion = funcion_actualizacion
    _page_ref = page
    print("[PROCESO] Actualizador del dashboard registrado")

async def actualizar_dashboard():
    """Actualiza el dashboard si hay una función registrada"""
    global _funcion_actualizacion, _page_ref
    if _funcion_actualizacion and _page_ref:
        try:
            # Pasar la función corrutina, no el resultado de ejecutarla
            print("[PROCESO] Ejecutando actualización del dashboard...")
            _page_ref.run_task(_funcion_actualizacion)
        except Exception as e:
            print(f"[ERROR] Error al actualizar dashboard: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[WARN] No hay función de actualización registrada")

def actualizar_dashboard_sincrono():
    """Versión síncrona para contextos no-async - Simplificada"""
    try:
        print("[PROCESO] Solicitud de actualización síncrona...")
        actualizar_dashboard()
    except Exception as e:
        print(f"[ERROR] Error en actualización síncrona: {e}")
