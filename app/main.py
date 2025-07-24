import flet as ft
from app.ui.login import login_view
from app.ui.principal import principal_view
from conexiones.firebase import db  # Importar la conexión a Firestore
import asyncio

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    page.window.resizable = True
    page.title = "TotalStock: Sistema de Inventario"

    # Función a ejecutar al iniciar sesión correctamente
    def cargar_pantalla_principal():
        page.controls.clear()
        asyncio.run(principal_view(page))
        page.update()

    # Mostrar la vista de login
    login_view(page, on_login_success=cargar_pantalla_principal)

ft.app(target=main)