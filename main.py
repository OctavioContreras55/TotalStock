import flet as ft
from app.ui_login import login_view
from app.ui_principal import principal_view

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK  # Establece el modo de tema
    page.window.maximized = True
    page.window.resizable = True
    page.title = "TotalStock: Sistema de Inventario"

    #Función a ejecutar al iniciar sesión correctamente
    def cargar_pantalla_principal():
        page.controls.clear()               # <-- limpiar la pantalla
        principal_view(page)                # <-- mostrar vista principal
        page.update()
        
    #Mostrar la vista de login
    login_view(page, on_login_success=cargar_pantalla_principal)
    
#Ejecutar la aplicación Flet como escritorio
ft.app(target=main)