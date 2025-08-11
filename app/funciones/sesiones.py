import flet as ft

# Variable global para almacenar la sesión actual
_usuario_actual = None

class SesionManager:
    """Clase para manejar la sesión del usuario actual"""
    
    @staticmethod
    def establecer_usuario(usuario_data):
        """Establece el usuario actual en la sesión"""
        global _usuario_actual
        _usuario_actual = usuario_data
    
    @staticmethod
    def obtener_usuario_actual():
        """Obtiene los datos del usuario actual"""
        global _usuario_actual
        return _usuario_actual
    
    @staticmethod
    def get_current_user():
        """Alias para compatibilidad - obtiene los datos del usuario actual"""
        return SesionManager.obtener_usuario_actual()
    
    @staticmethod
    def limpiar_sesion():
        """Limpia la sesión actual"""
        global _usuario_actual
        _usuario_actual = None

async def cerrar_sesion(page: ft.Page):
    """Cerrar sesión completa - limpia sesión local y única"""
    # Obtener el tema actual antes de limpiar la sesión
    from app.utils.temas import GestorTemas
    tema_actual = GestorTemas.obtener_tema_actual()
    
    # NUEVO: Obtener usuario actual antes de limpiar para cerrar sesión única
    usuario_actual = SesionManager.obtener_usuario_actual()
    nombre_usuario = None
    
    if usuario_actual:
        # Intentar diferentes formas de obtener el nombre del usuario
        if 'username' in usuario_actual:
            nombre_usuario = usuario_actual['username']
        elif 'nombre' in usuario_actual:
            nombre_usuario = usuario_actual['nombre']
        elif 'email' in usuario_actual:
            nombre_usuario = usuario_actual['email']
    
    print(f"[LOGOUT] Cerrando sesión para usuario: {nombre_usuario}")
    
    # Limpiar la sesión local
    SesionManager.limpiar_sesion()
    
    # NUEVO: Limpiar sesión única si hay usuario
    if nombre_usuario:
        try:
            from app.utils.sesiones_unicas import gestor_sesiones
            gestor_sesiones.cerrar_sesion(nombre_usuario)
            print(f"[LOGOUT] Sesión única cerrada para: {nombre_usuario}")
            
            # IMPORTANTE: También actualizar variable global en run.py
            import run
            if hasattr(run, '_usuario_actual_global'):
                run._usuario_actual_global = None
                print("[LOGOUT] Variable global de usuario limpiada")
                
        except Exception as e:
            print(f"[ERROR] Error al cerrar sesión única: {e}")
    
    # Limpiar cache de tema y establecer el tema actual como tema del login
    GestorTemas.limpiar_cache()
    GestorTemas.cambiar_tema_login(tema_actual)
    
    # Limpiar controles actuales
    page.controls.clear()

    # Volver a mostrar login
    async def cargar_pantalla_principal():
        from app.ui.principal import principal_view
        await principal_view(page)

    # Importar aquí para evitar import circular
    from app.ui.login import login_view
    login_view(page, on_login_success=cargar_pantalla_principal)
    page.update()
    
    print("[LOGOUT] Redirección al login completada")