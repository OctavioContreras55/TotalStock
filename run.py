#!/usr/bin/env python3
"""
TotalStock - Versión corregida para problemas de cierre/apertura
"""

import sys
import os
import atexit
import threading
import time

# Protección para ejecutables PyInstaller
def safe_print(mensaje):
    """Print seguro que funciona en desarrollo y ejecutables"""
    try:
        if sys.stdout:
            print(mensaje)
    except (AttributeError, OSError):
        pass

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Variable global para rastrear el estado de la aplicación
_app_running = False
_usuario_actual_global = None
_closing_app = False  # Nueva variable para evitar múltiples cierres

def cleanup_session():
    """Función de limpieza que se ejecuta al salir"""
    global _usuario_actual_global, _closing_app
    
    if _closing_app:  # Evitar múltiples ejecuciones
        return
    
    _closing_app = True
    safe_print("Ejecutando limpieza de sesion al salir...")
    
    try:
        from app.funciones.sesiones import SesionManager
        from app.utils.sesiones_unicas import gestor_sesiones
        
        # Método 1: Usar variable global
        usuario_para_cerrar = _usuario_actual_global
        
        # Método 2: Obtener desde SesionManager si no hay global
        if not usuario_para_cerrar:
            usuario_actual = SesionManager.obtener_usuario_actual()
            if usuario_actual:
                if 'username' in usuario_actual:
                    usuario_para_cerrar = usuario_actual['username']
                elif 'email' in usuario_actual:
                    usuario_para_cerrar = usuario_actual['email']
        
        # Cerrar sesión si hay usuario
        if usuario_para_cerrar:
            gestor_sesiones.cerrar_sesion(usuario_para_cerrar)
            safe_print(f"Sesion cerrada para: {usuario_para_cerrar}")
        
        # Limpiar archivo de bloqueo de instancia
        from app.utils.instancia_unica import instance_lock
        instance_lock._cleanup()
        
    except Exception as e:
        safe_print(f"Error durante la limpieza: {e}")

def limpiar_sesiones_zombie_startup():
    """Limpieza automática de sesiones zombie con timeout"""
    try:
        timeout_duration = 10
        start_time = time.time()
        
        while time.time() - start_time < timeout_duration:
            try:
                from app.utils.sesiones_unicas import gestor_sesiones
                resultado = gestor_sesiones.limpiar_sesiones_zombie()
                safe_print(f"Limpieza zombie: {resultado['mensaje']}")
                break
            except ImportError:
                time.sleep(0.5)
            except Exception as e:
                safe_print(f"Error en limpieza zombie: {e}")
                break
                
    except Exception as e:
        safe_print(f"Error general en limpieza zombie: {e}")

def monitor_app_exit():
    """Monitor que verifica si la app sigue corriendo y limpia sesiones zombie"""
    global _app_running
    last_check = time.time()
    
    while _app_running:
        time.sleep(30)
        current_time = time.time()
        
        if current_time - last_check > 60:
            try:
                from app.utils.sesiones_unicas import gestor_sesiones
                gestor_sesiones.limpiar_sesiones_zombie()
                last_check = current_time
            except:
                pass

# Registrar limpieza automática
atexit.register(cleanup_session)

def obtener_ruta_recurso(ruta_relativa):
    """Obtiene la ruta correcta para recursos, tanto en desarrollo como en ejecutable"""
    try:
        ruta_base = sys._MEIPASS
    except AttributeError:
        ruta_base = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(ruta_base, ruta_relativa)

def main():
    """Función principal con verificación de instancia única"""
    global _app_running, _closing_app
    _app_running = True
    _closing_app = False
    
    # Limpieza automática de sesiones zombie al iniciar
    limpiar_sesiones_zombie_startup()
    
    # Verificar instancia única ANTES de importar Flet
    from app.utils.instancia_unica import instance_lock
    
    # Verificar si ya hay una instancia ejecutándose
    if instance_lock.is_already_running():
        safe_print("TotalStock ya está ejecutándose.")
        safe_print("Enfocando ventana existente...")
        sys.exit(0)
    
    safe_print(f"Credenciales Firebase cargadas desde: {os.path.abspath('conexiones/credenciales_firebase.json')}")
    safe_print("Iniciando TotalStock...")
    safe_print("Sistema de Gestion de Inventario")
    safe_print("=" * 50)

    # Iniciar monitor de salida en segundo plano
    monitor_thread = threading.Thread(target=monitor_app_exit, daemon=True)
    monitor_thread.start()

    # Importar y ejecutar la aplicación
    import flet as ft
    from app.ui.login import login_view
    from app.ui.principal import principal_view
    from app.utils.temas import GestorTemas

    async def main_app(page: ft.Page):
        global _usuario_actual_global, _closing_app
        tema = GestorTemas.obtener_tema()
        
        # Configuración de la ventana
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = tema.BG_COLOR
        page.window.maximized = True
        page.window.resizable = True
        page.window.min_width = 1200
        page.window.min_height = 800
        page.title = "TotalStock: Sistema de Inventario"
        
        # NUEVO: Función simplificada de cierre
        async def on_window_event(e):
            """Manejar eventos de ventana - SIMPLIFICADO"""
            global _app_running, _closing_app
            
            # Solo procesar evento de cierre real
            if e.data == "close" and not _closing_app:
                safe_print("Cerrando aplicación...")
                _app_running = False
                _closing_app = True
                
                # Ejecutar limpieza
                cleanup_session()
                
                # Cerrar la página
                page.window.destroy()
        
        # SIMPLIFICADO: Solo un event handler
        page.window.on_event = on_window_event
        
        # Función para actualizar usuario global cuando haga login
        def actualizar_usuario_global():
            global _usuario_actual_global
            try:
                from app.funciones.sesiones import SesionManager
                usuario_actual = SesionManager.obtener_usuario_actual()
                
                if usuario_actual:
                    if 'username' in usuario_actual:
                        _usuario_actual_global = usuario_actual['username']
                    elif 'email' in usuario_actual:
                        _usuario_actual_global = usuario_actual['email']
                    elif 'nombre' in usuario_actual:
                        _usuario_actual_global = usuario_actual['nombre']
                    
                    safe_print(f"Usuario actualizado: {_usuario_actual_global}")
                    
            except Exception as e:
                safe_print(f"Error actualizando usuario global: {e}")
        
        # Configurar icono de la ventana
        try:
            ruta_icono = obtener_ruta_recurso("assets/logo.ico")
            if os.path.exists(ruta_icono):
                page.window.icon = ruta_icono
                safe_print(f"Icono de ventana configurado: {ruta_icono}")
            else:
                safe_print(f"No se encontró el icono en: {ruta_icono}")
        except Exception as e:
            safe_print(f"Error al configurar icono de ventana: {e}")

        # Función para enfocar ventana cuando se detecte otra instancia
        def enfocar_ventana():
            try:
                page.window.to_front()
                safe_print("Ventana enfocada por petición de otra instancia")
            except Exception as e:
                safe_print(f"Error enfocando ventana: {e}")
        
        # Iniciar listener para peticiones de enfoque
        instance_lock.start_listener(enfocar_ventana)
        
        # Función a ejecutar al iniciar sesión correctamente
        async def cargar_pantalla_principal():
            # Actualizar usuario global cuando haga login exitoso
            actualizar_usuario_global()
            
            page.controls.clear()
            await principal_view(page)
            page.update()

        # Limpiar controles y mostrar pantalla de login
        page.controls.clear()
        login_view(page, cargar_pantalla_principal)
        page.update()

    try:
        # Ejecutar la aplicación
        ft.app(target=main_app, port=0)
    except Exception as e:
        safe_print(f"Error en la aplicación: {e}")
    finally:
        # Asegurar limpieza al salir
        _app_running = False
        if not _closing_app:
            cleanup_session()
        safe_print("Aplicacion finalizando...")

if __name__ == "__main__":
    main()
