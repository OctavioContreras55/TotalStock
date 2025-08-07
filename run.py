#!/usr/bin/env python3
"""
Punto de entrada principal para TotalStock
"""

import sys
import os
import atexit
import threading
import time

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verificar instancia única ANTES de importar Flet
from app.utils.instancia_unica import instance_lock

# Variable global para rastrear el estado de la aplicación
_app_running = False
_usuario_actual_global = None

def cleanup_session():
    """Función de limpieza que se ejecuta al salir"""
    global _usuario_actual_global
    print("Ejecutando limpieza de sesion al salir...")
    
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
                elif 'nombre' in usuario_actual:
                    usuario_para_cerrar = usuario_actual['nombre']
        
        # Método 3: Buscar por proceso ID
        if not usuario_para_cerrar:
            usuario_para_cerrar = gestor_sesiones.obtener_usuario_actual_desde_archivo()
        
        # Cerrar sesión si encontramos usuario
        if usuario_para_cerrar:
            gestor_sesiones.cerrar_sesion(usuario_para_cerrar)
            print(f"Sesión cerrada automáticamente para: {usuario_para_cerrar}")
        else:
            print("ℹNo se encontró sesión activa para cerrar")
        
        # Limpiar sesión local
        SesionManager.limpiar_sesion()
        
        # Limpiar el lock de instancia única
        instance_lock.cleanup()
        print("Limpieza completada")
        
    except Exception as error:
        print(f"Error durante limpieza: {error}")

def limpiar_sesiones_zombie_startup():
    """Limpieza automática de sesiones zombie al iniciar la aplicación"""
    try:
        import subprocess
        
        print("Ejecutando limpieza automatica de sesiones zombie...")
        
        # Ejecutar script de limpieza zombie de forma silenciosa
        result = subprocess.run([
            sys.executable, "limpiar_zombie.py"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            # Buscar línea de resultado de limpieza
            for line in output_lines:
                if "Eliminadas" in line and "sesiones zombie" in line:
                    print(f"Resultado: {line}")
                    break
            else:
                print("Limpieza automatica completada")
        else:
            # Si hay error, no es crítico, solo informar
            print("Limpieza zombie: sin sesiones pendientes")
        
    except Exception as e:
        # No es crítico si falla la limpieza zombie al inicio
        print(f"Limpieza zombie automatica no disponible: {e}")

def monitor_app_exit():
    """Monitor que verifica si la app sigue corriendo y limpia sesiones zombie"""
    global _app_running
    proceso_actual = os.getpid()
    
    while _app_running:
        time.sleep(3)  # Verificar cada 3 segundos
    
    # Si llegamos aquí, la app dejó de correr
    print("Monitor detecto cierre de aplicacion")
    cleanup_session()

# Registrar limpieza automática
atexit.register(cleanup_session)

def main():
    """Función principal con verificación de instancia única"""
    global _app_running
    _app_running = True
    
    # Limpieza automática de sesiones zombie al iniciar
    limpiar_sesiones_zombie_startup()
    
    # Verificar si ya hay una instancia ejecutándose
    if instance_lock.is_already_running():
        print("TotalStock ya está ejecutándose.")
        print("Enfocando ventana existente...")
        input("Presiona Enter para cerrar...")
        sys.exit(0)
    
    print("Credenciales Firebase cargadas desde:", os.path.abspath("conexiones/credenciales_firebase.json"))
    print("Iniciando TotalStock...")
    print("Sistema de Gestion de Inventario")
    print("=" * 50)

    # Iniciar monitor de salida en segundo plano
    monitor_thread = threading.Thread(target=monitor_app_exit, daemon=True)
    monitor_thread.start()

    # Importar y ejecutar la aplicación
    import flet as ft
    from app.ui.login import login_view
    from app.ui.principal import principal_view
    from app.utils.temas import GestorTemas

    def obtener_ruta_recurso(ruta_relativa):
        """Obtiene la ruta correcta para recursos, tanto en desarrollo como en ejecutable"""
        try:
            # PyInstaller crea una carpeta temporal _MEIPASS cuando ejecuta
            ruta_base = sys._MEIPASS
        except AttributeError:
            # En desarrollo, usar la ruta actual
            ruta_base = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(ruta_base, ruta_relativa)

    async def main_app(page: ft.Page):
        global _usuario_actual_global
        tema = GestorTemas.obtener_tema()
        
        # Configuración de la ventana
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = tema.BG_COLOR
        page.window.maximized = True
        page.window.resizable = True
        page.window.min_width = 1200  # Ancho mínimo más amplio
        page.window.min_height = 800  # Alto mínimo más amplio
        page.title = "TotalStock: Sistema de Inventario"
        
        # Función para manejar cierre de aplicación (múltiples eventos)
        async def manejar_cierre_ventana(e):
            """Manejar diferentes eventos de cierre"""
            global _app_running, _usuario_actual_global
            
            print(f"Evento detectado: {e.data}")
            
            # Procesar eventos relacionados con cierre
            if e.data in ["close", "minimize", "window-event"]:
                print("Detectado posible cierre, registrando usuario actual...")
                
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
                        
                        print(f"Usuario registrado para limpieza: {_usuario_actual_global}")
                    
                    # Si es un cierre definitivo, ejecutar limpieza inmediata
                    if e.data == "close":
                        _app_running = False
                        cleanup_session()
                        
                except Exception as error:
                    print(f"Error registrando usuario: {error}")
        
        # Función especial para cuando la página se va a cerrar
        async def on_page_close(e):
            """Evento específico de cierre de página"""
            global _app_running
            print("Página cerrándose, iniciando limpieza...")
            _app_running = False
            cleanup_session()
        
        # Configurar múltiples tipos de eventos
        page.window.on_event = manejar_cierre_ventana
        page.on_window_event = manejar_cierre_ventana
        page.on_disconnect = on_page_close
        
        # Función para actualizar usuario global cuando haga login
        def actualizar_usuario_global():
            """Actualizar usuario global desde el SesionManager"""
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
                    
                    print(f"Usuario global actualizado: {_usuario_actual_global}")
                        
            except Exception as e:
                print(f"Error actualizando usuario global: {e}")
        
        # Configurar icono de la ventana
        try:
            ruta_icono = obtener_ruta_recurso("assets/logo.ico")
            if os.path.exists(ruta_icono):
                page.window.icon = ruta_icono
                print(f"Icono de ventana configurado: {ruta_icono}")
            else:
                print(f"No se encontró el icono en: {ruta_icono}")
        except Exception as e:
            print(f"Error al configurar icono de ventana: {e}")

        # Función para enfocar ventana cuando se detecte otra instancia
        def enfocar_ventana():
            try:
                page.window.to_front()
                print("Ventana enfocada por petición de otra instancia")
            except Exception as e:
                print(f"Error enfocando ventana: {e}")
        
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
        login_view(page, cargar_pantalla_principal)  # Quitar await porque login_view no es async
        page.update()

    try:
        # Ejecutar la aplicación
        ft.app(target=main_app, port=0)
    finally:
        # Asegurar limpieza al salir
        _app_running = False
        print("Aplicacion finalizando...")

if __name__ == "__main__":
    main()
