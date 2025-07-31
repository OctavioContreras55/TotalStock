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
    def limpiar_sesion():
        """Limpia la sesión actual"""
        global _usuario_actual
        _usuario_actual = None

async def cerrar_sesion(page: ft.Page):  # <-- CAMBIAR: Hacer función asíncrona
    # Obtener el tema actual antes de limpiar la sesión
    from app.utils.temas import GestorTemas
    tema_actual = GestorTemas.obtener_tema_actual()
    
    # Limpiar la sesión
    SesionManager.limpiar_sesion()
    
    # Limpiar cache de tema y establecer el tema actual como tema del login
    GestorTemas.limpiar_cache()
    GestorTemas.cambiar_tema_login(tema_actual)
    
    # Limpiar controles actuales
    page.controls.clear()

    # Volver a mostrar login
    async def cargar_pantalla_principal():  # <-- CAMBIAR: Hacer función asíncrona
        from app.ui.principal import principal_view
        await principal_view(page)  # <-- CAMBIAR: Usar await en lugar de asyncio.run()

    # Importar aquí para evitar import circular
    from app.ui.login import login_view
    login_view(page, on_login_success=cargar_pantalla_principal)
    page.update()