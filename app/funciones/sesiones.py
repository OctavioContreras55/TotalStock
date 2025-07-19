import flet as ft
from app.ui_login import login_view

def cerrar_sesion(page: ft.Page):
    # Limpiar controles actuales
    page.controls.clear()

    # Volver a mostrar login
    def cargar_pantalla_principal():
        from app.ui_principal import principal_view
        principal_view(page)

    login_view(page, on_login_success=cargar_pantalla_principal)
    page.update()