import flet as ft
from app.ui.login import login_view
from app.ui.principal import principal_view
from conexiones.firebase import db
from app.utils.temas import GestorTemas

async def main(page: ft.Page):  # <-- CAMBIAR: Hacer main asíncrono
    tema = GestorTemas.obtener_tema()
    
    # Configuración del tema
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = tema.BG_COLOR
    page.window.maximized = True
    page.window.resizable = True
    page.title = "TotalStock: Sistema de Inventario"

    # Función a ejecutar al iniciar sesión correctamente
    async def cargar_pantalla_principal():  # <-- CAMBIAR: Hacer función asíncrona
        page.controls.clear()
        await principal_view(page)  # <-- CAMBIAR: Con await
        page.update()

    # Mostrar la vista de login
    login_view(page, on_login_success=cargar_pantalla_principal)

ft.app(target=main)